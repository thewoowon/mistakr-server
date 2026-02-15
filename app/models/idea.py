from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class StartupIdea(Base):
    __tablename__ = "startup_idea"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # 기본 정보
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    stage = Column(String, nullable=True)  # idea, pre-seed, seed, ...
    revenue_model = Column(String, nullable=True)  # subscription, marketplace, ...

    # 팀 정보
    team_size = Column(Integer, nullable=True)
    has_technical_cofounder = Column(String, nullable=True)  # "yes", "no"
    team_experience = Column(String, nullable=True)  # first-time, serial, industry-expert

    # 비즈니스 정보
    monthly_burn = Column(Float, nullable=True)  # 월간 번레이트 (USD)
    runway_months = Column(Integer, nullable=True)
    has_revenue = Column(String, nullable=True)  # "yes", "no"
    target_market = Column(String, nullable=True)

    # 관계
    user = relationship("User", back_populates="ideas")
    consulting_sessions = relationship("ConsultingSession", back_populates="idea", cascade="all, delete-orphan")
