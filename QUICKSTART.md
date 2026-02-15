# Quick Start Guide

## 1. 의존성 설치

```bash
cd /Users/aepeul/dev/server/mistakr-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 환경 변수 설정

`.env` 파일 수정:

```env
# 필수
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ANTHROPIC_API_KEY=sk-ant-your-api-key

# OAuth (프론트 연동 시)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 3. 서버 실행

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 시작 시 DB 테이블 12개가 자동 생성된다.

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 4. 동작 확인

### 케이스 목록 조회 (인증 불필요)

```bash
curl http://localhost:8000/api/v1/cases
```

### 아이디어 생성 (인증 필요)

```bash
curl -X POST http://localhost:8000/api/v1/ideas \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FreshMeal",
    "industry": "food",
    "description": "신선 식재료 구독 서비스",
    "stage": "seed",
    "revenue_model": "subscription",
    "team_size": 4,
    "has_technical_cofounder": "yes",
    "monthly_burn": 15000,
    "runway_months": 8,
    "has_revenue": "no"
  }'
```

### AI 컨설팅 시작 (SSE 스트리밍)

```bash
curl -N -X POST http://localhost:8000/api/v1/consulting/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"idea_id": 1}'
```

4단계로 SSE 이벤트가 스트리밍된다:
1. `matching` - 유사 케이스 매칭
2. `analyzing` - Claude AI 분석 (텍스트 청크 전송)
3. `generating` - 결과 파싱 및 저장
4. `completed` - 전체 결과 전송

### 체크리스트 토글

```bash
curl -X PATCH http://localhost:8000/api/v1/consulting/sessions/1/checklist/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

## 5. DB 초기화 (필요 시)

```bash
RESET_DB=true uvicorn app.main:app --host 0.0.0.0 --port 8000
```

모든 테이블을 삭제 후 재생성한다.

## 문제 해결

### CORS 에러
[app/main.py](app/main.py)의 `allow_origins`에 프론트엔드 URL을 추가한다.

### Claude API 에러
`.env`의 `ANTHROPIC_API_KEY`가 올바른지 확인한다. 동기식 엔드포인트(`/consulting/sessions/sync`)로 먼저 테스트하면 디버그가 쉽다.

### Database locked
```bash
rm app/db/mistakr.db
# 서버 재시작하면 자동 재생성
```

## 다음 단계

1. Anthropic API 키 발급 및 설정
2. 실패 케이스 데이터 입력 (DB seed)
3. Railway 배포
4. 프론트엔드 mock 데이터 → 실제 API 전환
