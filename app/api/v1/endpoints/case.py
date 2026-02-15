from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.case_service import get_all_cases, get_case_detail, search_cases
from app.schemas.case import CaseListResponse

router = APIRouter()


@router.get("")
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """전체 케이스 목록 (인증 불필요)"""
    cases = get_all_cases(db, skip, limit)
    return JSONResponse(content={
        "data": [CaseListResponse.model_validate(c).model_dump(mode="json") for c in cases]
    })


@router.get("/search")
def search(
    q: str = Query("", min_length=0),
    industry: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """케이스 검색 (인증 불필요)"""
    cases = search_cases(db, q, industry)
    return JSONResponse(content={
        "data": [CaseListResponse.model_validate(c).model_dump(mode="json") for c in cases]
    })


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    """케이스 상세 조회 (인증 불필요)"""
    detail = get_case_detail(db, case_id)
    if not detail:
        return JSONResponse(content={"error": "Case not found"}, status_code=404)

    case = detail["case"]
    return JSONResponse(content={
        "data": {
            "id": case.id,
            "company_name": case.company_name,
            "industry": case.industry,
            "founded_year": case.founded_year,
            "failed_year": case.failed_year,
            "country": case.country,
            "one_liner": case.one_liner,
            "description": case.description,
            "logo_url": case.logo_url,
            "failure_types": case.failure_types or [],
            "stage": case.stage,
            "revenue_model": case.revenue_model,
            "total_funding": case.total_funding,
            "burn_rate": case.burn_rate,
            "runway_months": case.runway_months,
            "peak_employees": case.peak_employees,
            "team_size_at_failure": case.team_size_at_failure,
            "pivot_count": case.pivot_count,
            "peak_revenue": case.peak_revenue,
            "peak_valuation": case.peak_valuation,
            "timeline": case.timeline,
            "nodes": case.nodes,
            "edges": case.edges,
            "key_lessons": case.key_lessons,
            "sources": case.sources,
            "failure_causes": detail["failure_causes"],
            "warning_signs": detail["warning_signs"],
            "counterfactuals": detail["counterfactuals"],
            "competitors": detail["competitors"],
            "market_condition": detail["market_condition"],
            "created_at": case.created_at.isoformat() if case.created_at else None,
        }
    })
