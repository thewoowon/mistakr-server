from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class ConsultingSession(Base):
    __tablename__ = "consulting_session"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    idea_id = Column(Integer, ForeignKey("startup_idea.id"), nullable=False, index=True)

    # 상태
    status = Column(String, nullable=False, default="pending")  # pending, analyzing, completed, failed

    # 리스크 점수 (7개 카테고리)
    risk_overall = Column(Float, nullable=True)
    risk_pmf = Column(Float, nullable=True)
    risk_financial = Column(Float, nullable=True)
    risk_team = Column(Float, nullable=True)
    risk_market = Column(Float, nullable=True)
    risk_timing = Column(Float, nullable=True)
    risk_competition = Column(Float, nullable=True)
    risk_execution = Column(Float, nullable=True)

    # AI 분석 결과
    executive_summary = Column(Text, nullable=True)
    threats = Column(JSON, nullable=True)  # ["threat1", "threat2"]
    opportunities = Column(JSON, nullable=True)  # ["opp1", "opp2"]

    # 매칭된 케이스
    matched_cases = Column(JSON, nullable=True)  # [{case_id, similarity, match_reasons, key_lesson}]

    # 타임라인 예측
    timeline_predictions = Column(JSON, nullable=True)  # [{month, event, risk_level, confidence}]

    # 관계
    user = relationship("User", back_populates="consulting_sessions")
    idea = relationship("StartupIdea", back_populates="consulting_sessions")
    checklist_items = relationship("ChecklistItem", back_populates="session", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_item"

    session_id = Column(Integer, ForeignKey("consulting_session.id"), nullable=False, index=True)

    # 체크리스트 내용
    action = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    priority = Column(String, nullable=False, default="medium")  # critical, high, medium, low
    category = Column(String, nullable=True)  # financial, team, product, market, ...
    is_completed = Column(Boolean, nullable=False, default=False)

    # 관계
    session = relationship("ConsultingSession", back_populates="checklist_items")
