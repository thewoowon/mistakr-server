from sqlalchemy.orm import Session
from app.models.case import Case, FailureCause, WarningSign, Counterfactual, Competitor, MarketCondition


def get_all_cases(db: Session, skip: int = 0, limit: int = 50) -> list[Case]:
    return db.query(Case).order_by(Case.created_at.desc()).offset(skip).limit(limit).all()


def get_case_by_id(db: Session, case_id: int) -> Case | None:
    return db.query(Case).filter(Case.id == case_id).first()


def search_cases(db: Session, query: str, industry: str | None = None) -> list[Case]:
    q = db.query(Case)
    if query:
        q = q.filter(Case.company_name.ilike(f"%{query}%"))
    if industry:
        q = q.filter(Case.industry == industry)
    return q.order_by(Case.created_at.desc()).all()


def get_case_detail(db: Session, case_id: int) -> dict | None:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None

    failure_causes = db.query(FailureCause).filter(FailureCause.case_id == case_id).all()
    warning_signs = db.query(WarningSign).filter(WarningSign.case_id == case_id).all()
    counterfactuals = db.query(Counterfactual).filter(Counterfactual.case_id == case_id).all()
    competitors = db.query(Competitor).filter(Competitor.case_id == case_id).all()
    market_condition = db.query(MarketCondition).filter(MarketCondition.case_id == case_id).first()

    return {
        "case": case,
        "failure_causes": [
            {"category": fc.category, "title": fc.title, "description": fc.description,
             "severity": fc.severity, "was_preventable": fc.was_preventable}
            for fc in failure_causes
        ],
        "warning_signs": [
            {"category": ws.category, "signal": ws.signal,
             "appeared_month": ws.appeared_month, "was_ignored": ws.was_ignored}
            for ws in warning_signs
        ],
        "counterfactuals": [
            {"scenario": cf.scenario, "likely_outcome": cf.likely_outcome, "confidence": cf.confidence}
            for cf in counterfactuals
        ],
        "competitors": [
            {"name": c.name, "survived": c.survived, "advantage": c.advantage}
            for c in competitors
        ],
        "market_condition": {
            "tam": market_condition.tam,
            "growth_rate": market_condition.growth_rate,
            "competitor_count": market_condition.competitor_count,
            "regulatory_intensity": market_condition.regulatory_intensity,
            "market_timing": market_condition.market_timing,
        } if market_condition else None,
    }
