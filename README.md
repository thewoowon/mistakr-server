# Mistakr Backend Server

스타트업 실패 사례 분석 + AI 컨설팅 플랫폼 **Mistakr**의 FastAPI 백엔드 서버.

## Features

- **AI 실패 컨설팅**: Claude Sonnet으로 스타트업 아이디어 리스크 분석
- **SSE 스트리밍**: 실시간 분석 진행 상황 전송 (matching → analyzing → generating → completed)
- **케이스 매칭 엔진**: 규칙 기반 유사 실패 사례 매칭 (industry, stage, team, revenue model 가중치)
- **리스크 점수**: 7개 카테고리 (PMF, Financial, Team, Market, Timing, Competition, Execution) 0-100 점수
- **액션 체크리스트**: AI 생성 + 사용자 토글 가능
- **타임라인 예측**: 향후 18개월 리스크 이벤트 예측
- Google/Apple OAuth + JWT 인증
- SQLite + SQLAlchemy

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite + SQLAlchemy (async/sync)
- **AI**: Anthropic Claude API (Sonnet 4.5)
- **Authentication**: JWT (access 30min / refresh 7days) + Google/Apple OAuth
- **Streaming**: SSE (Server-Sent Events)

## Project Structure

```
mistakr-server/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── auth.py              # Google/Apple OAuth + JWT
│   │   ├── user.py              # 사용자 CRUD
│   │   ├── idea.py              # 스타트업 아이디어 CRUD
│   │   ├── consulting.py        # AI 컨설팅 세션 (SSE 스트리밍)
│   │   └── case.py              # 실패 케이스 목록/검색/상세
│   ├── models/
│   │   ├── user.py, token.py    # 인증 모델
│   │   ├── case.py              # Case + FailureCause, WarningSign, Counterfactual, Competitor, MarketCondition
│   │   ├── idea.py              # StartupIdea
│   │   └── consulting.py        # ConsultingSession, ChecklistItem
│   ├── schemas/                 # Pydantic request/response 모델
│   ├── services/
│   │   ├── auth_service.py      # OAuth 인증 로직
│   │   ├── user_service.py      # 사용자 비즈니스 로직
│   │   ├── idea_service.py      # 아이디어 CRUD
│   │   ├── case_service.py      # 케이스 조회
│   │   ├── matching_service.py  # 규칙 기반 매칭 엔진
│   │   ├── claude_service.py    # Claude API 통합
│   │   └── consulting_service.py # SSE 스트리밍 분석 플로우
│   ├── core/
│   │   ├── config.py            # Pydantic Settings
│   │   └── security.py          # JWT 토큰 처리
│   ├── db/
│   │   ├── base.py              # SQLAlchemy Base (auto tablename, timestamps)
│   │   └── session.py           # DB 엔진 및 세션
│   ├── dependencies.py          # FastAPI DI (get_db)
│   └── main.py                  # FastAPI app (lifespan, CORS, router)
├── .env                         # 환경 변수 (git 제외)
├── .env.example                 # 환경 변수 템플릿
├── requirements.txt             # Python 패키지
└── settings.py                  # 전역 상수
```

## API Endpoints

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/google` | - | Google 로그인 |
| POST | `/api/v1/auth/apple` | - | Apple 로그인 |
| POST | `/api/v1/auth/token/reissue` | - | 토큰 갱신 |
| POST | `/api/v1/auth/logout` | Bearer | 로그아웃 |

### User

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/users/me` | Bearer | 내 정보 조회 |
| DELETE | `/api/v1/users/me` | Bearer | 계정 삭제 |

### Startup Ideas

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/ideas` | Bearer | 아이디어 생성 |
| GET | `/api/v1/ideas` | Bearer | 내 아이디어 목록 |
| GET | `/api/v1/ideas/{id}` | Bearer | 아이디어 상세 |
| PUT | `/api/v1/ideas/{id}` | Bearer | 수정 |
| DELETE | `/api/v1/ideas/{id}` | Bearer | 삭제 |

### AI Consulting

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/consulting/sessions` | Bearer | 새 컨설팅 (SSE 스트리밍) |
| POST | `/api/v1/consulting/sessions/sync` | Bearer | 동기식 컨설팅 (테스트용) |
| GET | `/api/v1/consulting/sessions` | Bearer | 내 세션 목록 |
| GET | `/api/v1/consulting/sessions/{id}` | Bearer | 세션 상세 |
| PATCH | `/api/v1/consulting/sessions/{id}/checklist/{item_id}` | Bearer | 체크리스트 토글 |

### Cases (실패 사례)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/cases` | - | 전체 케이스 목록 |
| GET | `/api/v1/cases/search?q=&industry=` | - | 검색 |
| GET | `/api/v1/cases/{id}` | - | 케이스 상세 (enriched data 포함) |

## SSE Streaming Protocol

`POST /api/v1/consulting/sessions` 요청 시 SSE 스트리밍으로 응답:

```
Phase 1: matching
data: {"phase": "matching", "data": {"progress": 0}}
data: {"phase": "matching", "data": {"progress": 100, "matched_cases": [...]}}

Phase 2: analyzing (Claude API 스트리밍)
data: {"phase": "analyzing", "data": {"progress": 0}}
data: {"phase": "analyzing", "chunk": "리스크 분석 텍스트..."}

Phase 3: generating
data: {"phase": "generating", "data": {"progress": 50}}
data: {"phase": "generating", "data": {"progress": 100}}

Phase 4: completed
data: {"phase": "completed", "data": {"session_id": 1, "risk_scores": {...}, ...}}
```

## Matching Algorithm

규칙 기반 가중치 (Phase 2, 데이터 50개 이상 시 pgvector 전환 예정):

| Factor | Weight | Condition |
|--------|--------|-----------|
| Industry | +0.30 | 동일 산업 |
| Failure Type | +0.20 each (max 0.40) | 리스크 패턴 일치 |
| Stage | +0.15 | 동일 단계 |
| Team Size | +0.10 | 유사 규모 (ratio > 0.5) |
| Revenue Model | +0.10 | 동일 수익 모델 |

## Database Schema

12개 테이블:

- `user` - 사용자
- `token` - Refresh token
- `case` - 실패 사례 (정량 데이터, 타임라인, 노드 그래프 포함)
- `failure_cause` - 실패 원인 (severity: critical/major/contributing)
- `warning_sign` - 경고 신호 (6개 카테고리)
- `counterfactual` - 반사실적 분석 ("만약 ~했다면")
- `competitor` - 경쟁사 정보
- `market_condition` - 시장 환경 (TAM, 성장률, 규제 강도)
- `startup_idea` - 사용자 스타트업 아이디어
- `consulting_session` - AI 컨설팅 세션 (7개 리스크 점수, 매칭 결과, 예측)
- `checklist_item` - 액션 체크리스트 (priority + 완료 여부)

## Token Management

- **Access Token**: 30분, `Authorization: Bearer {token}` 헤더
- **Refresh Token**: 7일, DB 저장, rotation 방식 (갱신 시 새 토큰 발급)
- **Payload**: `{"sub": "user@email.com", "user_id": 1, "exp": timestamp}`

## Deployment

Railway에 배포 (기존 인프라 활용):

```bash
# 환경 변수 설정
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./app/db/mistakr.db
```

## License

MIT
