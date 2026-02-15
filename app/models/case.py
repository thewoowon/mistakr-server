from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Case(Base):
    __tablename__ = "case"

    # 기본 정보
    company_name = Column(String, nullable=False, index=True)
    industry = Column(String, nullable=False, index=True)
    founded_year = Column(Integer, nullable=True)
    failed_year = Column(Integer, nullable=True)
    country = Column(String, nullable=True)
    one_liner = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)

    # 분류
    failure_types = Column(JSON, nullable=False, default=list)  # ["market-fit", "financial"]
    stage = Column(String, nullable=True)  # pre-seed, seed, series-a, ...
    revenue_model = Column(String, nullable=True)  # subscription, marketplace, ...

    # 정량 데이터 (CompanyMetrics)
    total_funding = Column(Float, nullable=True)  # 총 투자 유치 (USD)
    burn_rate = Column(Float, nullable=True)  # 월간 번레이트 (USD)
    runway_months = Column(Integer, nullable=True)  # 남은 런웨이
    peak_employees = Column(Integer, nullable=True)  # 최대 직원 수
    team_size_at_failure = Column(Integer, nullable=True)
    pivot_count = Column(Integer, nullable=True, default=0)
    peak_revenue = Column(Float, nullable=True)
    peak_valuation = Column(Float, nullable=True)

    # 타임라인
    timeline = Column(JSON, nullable=True)  # [{date, event, type}]

    # 노드 그래프 데이터
    nodes = Column(JSON, nullable=True)  # [{id, label, type, x, y}]
    edges = Column(JSON, nullable=True)  # [{source, target, label}]

    # 핵심 교훈
    key_lessons = Column(JSON, nullable=True)  # ["lesson1", "lesson2"]
    sources = Column(JSON, nullable=True)  # ["url1", "url2"]

    # 관계
    failure_causes = relationship("FailureCause", back_populates="case", cascade="all, delete-orphan")
    warning_signs = relationship("WarningSign", back_populates="case", cascade="all, delete-orphan")
    counterfactuals = relationship("Counterfactual", back_populates="case", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="case", cascade="all, delete-orphan")
    market_condition = relationship("MarketCondition", back_populates="case", uselist=False, cascade="all, delete-orphan")


class FailureCause(Base):
    __tablename__ = "failure_cause"

    case_id = Column(Integer, ForeignKey("case.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # market-fit, financial, team, ...
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False, default="major")  # critical, major, contributing
    was_preventable = Column(Boolean, nullable=True)

    case = relationship("Case", back_populates="failure_causes")


class WarningSign(Base):
    __tablename__ = "warning_sign"

    case_id = Column(Integer, ForeignKey("case.id"), nullable=False, index=True)
    category = Column(String, nullable=False)  # financial, operational, market, team, product, legal
    signal = Column(String, nullable=False)
    appeared_month = Column(Integer, nullable=True)  # 실패 전 몇 개월
    was_ignored = Column(Boolean, nullable=True)

    case = relationship("Case", back_populates="warning_signs")


class Counterfactual(Base):
    __tablename__ = "counterfactual"

    case_id = Column(Integer, ForeignKey("case.id"), nullable=False, index=True)
    scenario = Column(String, nullable=False)  # "만약 ~했다면"
    likely_outcome = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)  # 0-1

    case = relationship("Case", back_populates="counterfactuals")


class Competitor(Base):
    __tablename__ = "competitor"

    case_id = Column(Integer, ForeignKey("case.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    survived = Column(Boolean, nullable=True)
    advantage = Column(String, nullable=True)  # 경쟁 우위 요인

    case = relationship("Case", back_populates="competitors")


class MarketCondition(Base):
    __tablename__ = "market_condition"

    case_id = Column(Integer, ForeignKey("case.id"), nullable=False, index=True)
    tam = Column(Float, nullable=True)  # Total Addressable Market (USD)
    growth_rate = Column(Float, nullable=True)  # 시장 성장률 (%)
    competitor_count = Column(Integer, nullable=True)
    regulatory_intensity = Column(String, nullable=True)  # low, medium, high
    market_timing = Column(String, nullable=True)  # too-early, right, too-late

    case = relationship("Case", back_populates="market_condition")
