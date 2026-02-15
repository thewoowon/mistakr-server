"""
컨설팅 세션 관리 서비스.
매칭 → Claude 분석 → 결과 저장 플로우 조율.
"""

import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.consulting import ConsultingSession, ChecklistItem
from app.models.idea import StartupIdea
from app.services.matching_service import find_matching_cases
from app.services.claude_service import analyze_idea, analyze_idea_streaming


def create_session(db: Session, user_id: int, idea_id: int) -> ConsultingSession:
    """새 컨설팅 세션 생성."""
    idea = db.query(StartupIdea).filter(
        StartupIdea.id == idea_id,
        StartupIdea.user_id == user_id,
    ).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    session = ConsultingSession(
        user_id=user_id,
        idea_id=idea_id,
        status="pending",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def run_analysis(db: Session, session_id: int, user_id: int) -> ConsultingSession:
    """동기식 분석 실행 (non-streaming)."""
    session = db.query(ConsultingSession).filter(
        ConsultingSession.id == session_id,
        ConsultingSession.user_id == user_id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    idea = db.query(StartupIdea).filter(StartupIdea.id == session.idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Phase 1: 매칭
    session.status = "analyzing"
    db.commit()

    matched = find_matching_cases(db, idea)
    session.matched_cases = matched

    # Phase 2: Claude 분석
    try:
        result = analyze_idea(idea, matched)
    except Exception as e:
        session.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # Phase 3: 결과 저장
    scores = result.get("risk_scores", {})
    session.risk_overall = scores.get("overall", 0)
    session.risk_pmf = scores.get("pmf", 0)
    session.risk_financial = scores.get("financial", 0)
    session.risk_team = scores.get("team", 0)
    session.risk_market = scores.get("market", 0)
    session.risk_timing = scores.get("timing", 0)
    session.risk_competition = scores.get("competition", 0)
    session.risk_execution = scores.get("execution", 0)

    session.executive_summary = result.get("executive_summary", "")
    session.threats = result.get("threats", [])
    session.opportunities = result.get("opportunities", [])
    session.timeline_predictions = result.get("timeline_predictions", [])

    # 체크리스트 저장
    for item in result.get("checklist", []):
        checklist_item = ChecklistItem(
            session_id=session.id,
            action=item.get("action", ""),
            reason=item.get("reason", ""),
            priority=item.get("priority", "medium"),
            category=item.get("category", ""),
        )
        db.add(checklist_item)

    session.status = "completed"
    db.commit()
    db.refresh(session)
    return session


def run_analysis_sse(db: Session, session_id: int, user_id: int):
    """SSE 스트리밍 분석 제너레이터."""
    session = db.query(ConsultingSession).filter(
        ConsultingSession.id == session_id,
        ConsultingSession.user_id == user_id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    idea = db.query(StartupIdea).filter(StartupIdea.id == session.idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Phase 1: 매칭
    yield f"data: {json.dumps({'phase': 'matching', 'data': {'progress': 0}})}\n\n"

    session.status = "analyzing"
    db.commit()

    matched = find_matching_cases(db, idea)
    session.matched_cases = matched
    db.commit()

    yield f"data: {json.dumps({'phase': 'matching', 'data': {'progress': 100, 'matched_cases': matched}})}\n\n"

    # Phase 2: 분석 (스트리밍)
    yield f"data: {json.dumps({'phase': 'analyzing', 'data': {'progress': 0}})}\n\n"

    accumulated_text = ""
    try:
        for chunk in analyze_idea_streaming(idea, matched):
            accumulated_text += chunk
            yield f"data: {json.dumps({'phase': 'analyzing', 'chunk': chunk})}\n\n"
    except Exception as e:
        session.status = "failed"
        db.commit()
        yield f"data: {json.dumps({'phase': 'error', 'data': {'message': str(e)}})}\n\n"
        return

    # Phase 3: 파싱 및 저장
    yield f"data: {json.dumps({'phase': 'generating', 'data': {'progress': 50}})}\n\n"

    try:
        # JSON 추출
        response_text = accumulated_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                elif line.startswith("```") and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        result = json.loads(response_text)

        # 결과 저장
        scores = result.get("risk_scores", {})
        session.risk_overall = scores.get("overall", 0)
        session.risk_pmf = scores.get("pmf", 0)
        session.risk_financial = scores.get("financial", 0)
        session.risk_team = scores.get("team", 0)
        session.risk_market = scores.get("market", 0)
        session.risk_timing = scores.get("timing", 0)
        session.risk_competition = scores.get("competition", 0)
        session.risk_execution = scores.get("execution", 0)

        session.executive_summary = result.get("executive_summary", "")
        session.threats = result.get("threats", [])
        session.opportunities = result.get("opportunities", [])
        session.timeline_predictions = result.get("timeline_predictions", [])

        for item in result.get("checklist", []):
            checklist_item = ChecklistItem(
                session_id=session.id,
                action=item.get("action", ""),
                reason=item.get("reason", ""),
                priority=item.get("priority", "medium"),
                category=item.get("category", ""),
            )
            db.add(checklist_item)

        session.status = "completed"
        db.commit()
        db.refresh(session)

        yield f"data: {json.dumps({'phase': 'generating', 'data': {'progress': 100}})}\n\n"

    except json.JSONDecodeError as e:
        session.status = "failed"
        db.commit()
        yield f"data: {json.dumps({'phase': 'error', 'data': {'message': f'JSON parsing failed: {str(e)}'}})}\n\n"
        return

    # Phase 4: 완료 — 전체 결과 전송
    checklist_items = db.query(ChecklistItem).filter(ChecklistItem.session_id == session.id).all()

    final_data = {
        "session_id": session.id,
        "risk_scores": {
            "overall": session.risk_overall,
            "pmf": session.risk_pmf,
            "financial": session.risk_financial,
            "team": session.risk_team,
            "market": session.risk_market,
            "timing": session.risk_timing,
            "competition": session.risk_competition,
            "execution": session.risk_execution,
        },
        "executive_summary": session.executive_summary,
        "threats": session.threats,
        "opportunities": session.opportunities,
        "matched_cases": session.matched_cases,
        "timeline_predictions": session.timeline_predictions,
        "checklist": [
            {
                "id": ci.id,
                "action": ci.action,
                "reason": ci.reason,
                "priority": ci.priority,
                "category": ci.category,
                "is_completed": ci.is_completed,
            }
            for ci in checklist_items
        ],
    }

    yield f"data: {json.dumps({'phase': 'completed', 'data': final_data})}\n\n"


def get_user_sessions(db: Session, user_id: int) -> List[dict]:
    """사용자의 컨설팅 세션 목록 조회."""
    sessions = db.query(ConsultingSession).filter(
        ConsultingSession.user_id == user_id,
    ).order_by(ConsultingSession.created_at.desc()).all()

    result = []
    for s in sessions:
        idea = db.query(StartupIdea).filter(StartupIdea.id == s.idea_id).first()
        checklist = db.query(ChecklistItem).filter(ChecklistItem.session_id == s.id).all()
        result.append({
            "id": s.id,
            "idea_id": s.idea_id,
            "idea_name": idea.name if idea else "Unknown",
            "status": s.status,
            "risk_overall": s.risk_overall,
            "checklist_total": len(checklist),
            "checklist_completed": sum(1 for c in checklist if c.is_completed),
            "created_at": s.created_at,
        })
    return result


def get_session_detail(db: Session, session_id: int, user_id: int) -> Optional[dict]:
    """세션 상세 조회."""
    session = db.query(ConsultingSession).filter(
        ConsultingSession.id == session_id,
        ConsultingSession.user_id == user_id,
    ).first()
    if not session:
        return None

    checklist = db.query(ChecklistItem).filter(ChecklistItem.session_id == session_id).all()

    return {
        "id": session.id,
        "idea_id": session.idea_id,
        "status": session.status,
        "risk_score": {
            "overall": session.risk_overall,
            "pmf": session.risk_pmf,
            "financial": session.risk_financial,
            "team": session.risk_team,
            "market": session.risk_market,
            "timing": session.risk_timing,
            "competition": session.risk_competition,
            "execution": session.risk_execution,
        } if session.risk_overall is not None else None,
        "executive_summary": session.executive_summary,
        "threats": session.threats,
        "opportunities": session.opportunities,
        "matched_cases": session.matched_cases,
        "timeline_predictions": session.timeline_predictions,
        "checklist": [
            {
                "id": ci.id,
                "action": ci.action,
                "reason": ci.reason,
                "priority": ci.priority,
                "category": ci.category,
                "is_completed": ci.is_completed,
            }
            for ci in checklist
        ],
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


def toggle_checklist_item(db: Session, session_id: int, item_id: int, user_id: int, is_completed: bool):
    """체크리스트 항목 토글."""
    session = db.query(ConsultingSession).filter(
        ConsultingSession.id == session_id,
        ConsultingSession.user_id == user_id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    item = db.query(ChecklistItem).filter(
        ChecklistItem.id == item_id,
        ChecklistItem.session_id == session_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    item.is_completed = is_completed
    db.commit()
    db.refresh(item)
    return item
