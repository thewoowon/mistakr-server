from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.consulting import ConsultingRequest, ChecklistToggle
from app.services.consulting_service import (
    create_session, run_analysis, run_analysis_sse,
    get_user_sessions, get_session_detail, toggle_checklist_item,
)

router = APIRouter()


@router.post("/sessions")
def create_consulting_session(
    req: ConsultingRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """새 컨설팅 세션 생성 및 SSE 스트리밍 분석 시작"""
    session = create_session(db, user_id, req.idea_id)

    return StreamingResponse(
        run_analysis_sse(db, session.id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": str(session.id),
        },
    )


@router.post("/sessions/sync")
def create_consulting_session_sync(
    req: ConsultingRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """동기식 컨설팅 (SSE 없이, 테스트/디버그용)"""
    session = create_session(db, user_id, req.idea_id)
    session = run_analysis(db, session.id, user_id)
    detail = get_session_detail(db, session.id, user_id)
    return JSONResponse(content={"data": detail})


@router.get("/sessions")
def list_sessions(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """내 컨설팅 세션 목록"""
    sessions = get_user_sessions(db, user_id)
    # datetime을 JSON serializable하게 변환
    for s in sessions:
        if s.get("created_at"):
            s["created_at"] = s["created_at"].isoformat()
    return JSONResponse(content={"data": sessions})


@router.get("/sessions/{session_id}")
def get_session(
    session_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """세션 상세 조회"""
    detail = get_session_detail(db, session_id, user_id)
    if not detail:
        return JSONResponse(content={"error": "Session not found"}, status_code=404)

    # datetime 변환
    if detail.get("created_at"):
        detail["created_at"] = detail["created_at"].isoformat()
    if detail.get("updated_at"):
        detail["updated_at"] = detail["updated_at"].isoformat()

    return JSONResponse(content={"data": detail})


@router.patch("/sessions/{session_id}/checklist/{item_id}")
def toggle_checklist(
    session_id: int,
    item_id: int,
    body: ChecklistToggle,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """체크리스트 항목 토글"""
    item = toggle_checklist_item(db, session_id, item_id, user_id, body.is_completed)
    return JSONResponse(content={
        "data": {
            "id": item.id,
            "action": item.action,
            "is_completed": item.is_completed,
        }
    })
