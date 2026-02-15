"""
규칙 기반 케이스 매칭 엔진.
Phase 2에서는 규칙 기반으로 시작, 데이터 50개 이상 시 pgvector 임베딩으로 전환.

가중치:
- industry 일치: +0.30
- failureType 겹침: +0.20 (each)
- stage 일치: +0.15
- teamSize 유사: +0.10
- revenueModel 일치: +0.10
- 기타 보너스: +0.15
"""

from typing import List, Tuple
from app.models.case import Case
from app.models.idea import StartupIdea
from sqlalchemy.orm import Session


def calculate_similarity(idea: StartupIdea, case: Case) -> Tuple[float, List[str]]:
    """아이디어와 케이스 간 유사도 계산. (score, match_reasons) 반환."""
    score = 0.0
    reasons = []

    # Industry 일치 (+0.30)
    if idea.industry and case.industry:
        if idea.industry.lower() == case.industry.lower():
            score += 0.30
            reasons.append(f"동일 산업: {idea.industry}")

    # Failure types와 아이디어 특성 매칭 (+0.20 each, max 0.40)
    failure_types = case.failure_types or []
    type_bonus = 0.0

    # 번레이트 높고 런웨이 짧으면 financial 실패와 매칭
    if idea.monthly_burn and idea.runway_months:
        if idea.runway_months <= 6 and "financial" in failure_types:
            type_bonus += 0.20
            reasons.append("재정적 리스크 유사")

    # 기술 공동창업자 없으면 team 실패와 매칭
    if idea.has_technical_cofounder == "no" and "team" in failure_types:
        type_bonus += 0.20
        reasons.append("팀 구성 리스크 유사")

    # PMF 관련
    if idea.has_revenue == "no" and "market-fit" in failure_types:
        type_bonus += 0.20
        reasons.append("PMF 미달성 유사")

    score += min(type_bonus, 0.40)

    # Stage 일치 (+0.15)
    if idea.stage and case.stage:
        if idea.stage.lower() == case.stage.lower():
            score += 0.15
            reasons.append(f"동일 단계: {idea.stage}")

    # Team size 유사 (+0.10)
    if idea.team_size and case.peak_employees:
        ratio = min(idea.team_size, case.peak_employees) / max(idea.team_size, case.peak_employees)
        if ratio > 0.5:
            score += 0.10 * ratio
            reasons.append("유사 팀 규모")

    # Revenue model 일치 (+0.10)
    if idea.revenue_model and case.revenue_model:
        if idea.revenue_model.lower() == case.revenue_model.lower():
            score += 0.10
            reasons.append(f"동일 수익 모델: {idea.revenue_model}")

    # 점수 클램프 0-1
    score = min(max(score, 0.0), 1.0)

    return score, reasons


def find_matching_cases(
    db: Session,
    idea: StartupIdea,
    top_k: int = 5,
    min_similarity: float = 0.15,
) -> List[dict]:
    """아이디어에 가장 유사한 케이스 top_k개 반환."""
    cases = db.query(Case).all()

    scored = []
    for case in cases:
        similarity, reasons = calculate_similarity(idea, case)
        if similarity >= min_similarity:
            scored.append({
                "case_id": case.id,
                "company_name": case.company_name,
                "similarity": round(similarity * 100, 1),  # 퍼센트
                "match_reasons": reasons,
                "key_lesson": (case.key_lessons or [""])[0] if case.key_lessons else "",
            })

    # 유사도 높은 순 정렬
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]
