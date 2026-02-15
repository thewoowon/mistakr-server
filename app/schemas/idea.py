from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IdeaCreate(BaseModel):
    name: str
    industry: str
    description: Optional[str] = None
    stage: Optional[str] = None
    revenue_model: Optional[str] = None
    team_size: Optional[int] = None
    has_technical_cofounder: Optional[str] = None
    team_experience: Optional[str] = None
    monthly_burn: Optional[float] = None
    runway_months: Optional[int] = None
    has_revenue: Optional[str] = None
    target_market: Optional[str] = None


class IdeaUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    revenue_model: Optional[str] = None
    team_size: Optional[int] = None
    has_technical_cofounder: Optional[str] = None
    team_experience: Optional[str] = None
    monthly_burn: Optional[float] = None
    runway_months: Optional[int] = None
    has_revenue: Optional[str] = None
    target_market: Optional[str] = None


class IdeaResponse(BaseModel):
    id: int
    name: str
    industry: str
    description: Optional[str]
    stage: Optional[str]
    revenue_model: Optional[str]
    team_size: Optional[int]
    has_technical_cofounder: Optional[str]
    team_experience: Optional[str]
    monthly_burn: Optional[float]
    runway_months: Optional[int]
    has_revenue: Optional[str]
    target_market: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
