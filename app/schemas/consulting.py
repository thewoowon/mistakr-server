from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConsultingRequest(BaseModel):
    idea_id: int


class FollowUpRequest(BaseModel):
    question: str


class ChecklistToggle(BaseModel):
    is_completed: bool


class MatchedCaseResponse(BaseModel):
    case_id: int
    company_name: str
    similarity: float
    match_reasons: List[str]
    key_lesson: str


class TimelinePredictionResponse(BaseModel):
    month: int
    event: str
    risk_level: str  # low, medium, high, critical
    confidence: float


class ChecklistItemResponse(BaseModel):
    id: int
    action: str
    reason: Optional[str]
    priority: str
    category: Optional[str]
    is_completed: bool

    class Config:
        from_attributes = True


class RiskScoreResponse(BaseModel):
    overall: float
    pmf: float
    financial: float
    team: float
    market: float
    timing: float
    competition: float
    execution: float


class ConsultingSessionResponse(BaseModel):
    id: int
    idea_id: int
    status: str
    risk_score: Optional[RiskScoreResponse] = None
    executive_summary: Optional[str] = None
    threats: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    matched_cases: Optional[List[MatchedCaseResponse]] = None
    timeline_predictions: Optional[List[TimelinePredictionResponse]] = None
    checklist: Optional[List[ChecklistItemResponse]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsultingSessionListResponse(BaseModel):
    id: int
    idea_id: int
    idea_name: str
    status: str
    risk_overall: Optional[float] = None
    checklist_total: int = 0
    checklist_completed: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
