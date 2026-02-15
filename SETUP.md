# Mistakr 서버 설정 가이드

## 1. 의존성 설치

```bash
pip install -r requirements.txt
```

## 2. 환경 변수 설정

`.env` 파일에 Anthropic API 키를 추가:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key
```

## 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버 시작 시 12개 테이블이 자동 생성된다.

## AI 컨설팅 플로우

1. **아이디어 입력**: 사용자가 스타트업 아이디어 정보 입력
2. **컨설팅 요청**:
   ```json
   POST /api/v1/consulting/sessions
   {"idea_id": 1}
   ```
3. **SSE 스트리밍 4단계**:
   - matching: 규칙 기반으로 유사 실패 사례 매칭
   - analyzing: Claude Sonnet이 리스크 분석
   - generating: 결과 파싱 및 체크리스트 저장
   - completed: 전체 결과 전송
4. **결과**: 7개 카테고리 리스크 점수, 위협/기회, 타임라인 예측, 액션 체크리스트

## Claude API 모델

- **Claude Sonnet 4.5**: 리스크 분석 + 체크리스트 생성 (품질 vs 비용 균형)

`.env`의 `ANTHROPIC_API_KEY`만 설정하면 바로 동작한다.
