# MovieAndMe 서버 설정 가이드

## 1. 의존성 설치

```bash
pip install -r requirements.txt
```

## 2. 환경 변수 설정

`.env` 파일에 OpenAI API 키를 추가하세요:

```bash
# OpenAI Settings
OPENAI_API_KEY=sk-your-actual-openai-api-key
OPENAI_MODEL=gpt-4o-mini  # 또는 gpt-3.5-turbo
```

## 3. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 테이블을 생성합니다:

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Add diary, movie, ticket models"

# 마이그레이션 실행
alembic upgrade head
```

## 4. 영화 샘플 데이터 추가

```bash
python scripts/seed_movies.py
```

**주의**: 현재 `seed_movies.py`에는 10개의 샘플 영화만 있습니다.
100개의 영화 데이터를 추가하려면 `SAMPLE_MOVIES` 리스트를 확장하세요.

## 5. 서버 실행

```bash
uvicorn app.main:app --reload
```

## API 엔드포인트

### 일기 (Diaries)

- `POST /api/v1/diaries/` - 일기 작성
- `GET /api/v1/diaries/` - 내 모든 일기 조회
- `GET /api/v1/diaries/today` - 오늘 일기 조회
- `GET /api/v1/diaries/date/{date}` - 특정 날짜 일기 조회

### 영화 추천 (Movies)

- `POST /api/v1/movies/recommend` - 일기+purpose로 영화 추천 (OpenAI 사용)
- `POST /api/v1/movies/recommend-by-keywords` - 키워드로 직접 추천
- `POST /api/v1/movies/` - 영화 생성 (관리자)
- `GET /api/v1/movies/` - 모든 영화 조회
- `GET /api/v1/movies/{id}` - 영화 상세 조회

### 티켓 (Tickets)

- `POST /api/v1/tickets/` - 티켓 생성 및 할당
- `GET /api/v1/tickets/my-tickets` - 내 티켓 목록
- `GET /api/v1/tickets/{id}` - 티켓 상세 조회

## 영화 추천 플로우

1. **일기 작성**: 사용자가 일기 내용과 purpose를 입력
2. **영화 추천 요청**:
   ```json
   POST /api/v1/movies/recommend
   {
     "diary_content": "오늘은 정말 힘든 하루였다...",
     "purpose": "기분 전환하고 싶어요",
     "top_k": 5
   }
   ```
3. **OpenAI 키워드 추출**: LLM이 일기와 purpose를 분석하여 키워드 추출
4. **영화 매칭**: 추출된 키워드와 영화 keywords를 비교하여 점수 계산
5. **응답**:
   ```json
   {
     "movies": [...],  // 추천 영화 목록
     "keywords": ["힐링", "코미디", "일상", ...]  // 추출된 키워드
   }
   ```

## OpenAI 모델 선택

- **gpt-4o-mini**: 빠르고 저렴, 키워드 추출에 충분 (권장)
- **gpt-3.5-turbo**: 더 빠르고 더 저렴
- **gpt-4**: 더 정확하지만 비쌈

`.env` 파일의 `OPENAI_MODEL`을 변경하여 선택할 수 있습니다.

## 비용 절감 팁

1. OpenAI API 사용량 모니터링
2. 필요시 키워드 캐싱 추가
3. 비슷한 일기에 대해 키워드 재사용 고려
