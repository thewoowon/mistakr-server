from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CaseListResponse(BaseModel):
    id: int
    company_name: str
    industry: str
    one_liner: Optional[str]
    failure_types: List[str]
    stage: Optional[str]
    founded_year: Optional[int]
    failed_year: Optional[int]
    total_funding: Optional[float]
    logo_url: Optional[str]

    class Config:
        from_attributes = True


class CaseDetailResponse(BaseModel):
    id: int
    company_name: str
    industry: str
    founded_year: Optional[int]
    failed_year: Optional[int]
    country: Optional[str]
    one_liner: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    failure_types: List[str]
    stage: Optional[str]
    revenue_model: Optional[str]
    total_funding: Optional[float]
    burn_rate: Optional[float]
    runway_months: Optional[int]
    peak_employees: Optional[int]
    team_size_at_failure: Optional[int]
    pivot_count: Optional[int]
    peak_revenue: Optional[float]
    peak_valuation: Optional[float]
    timeline: Optional[list]
    nodes: Optional[list]
    edges: Optional[list]
    key_lessons: Optional[List[str]]
    sources: Optional[List[str]]
    failure_causes: Optional[list] = None
    warning_signs: Optional[list] = None
    counterfactuals: Optional[list] = None
    competitors: Optional[list] = None
    market_condition: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
