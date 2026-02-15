"""
Claude API 통합 서비스.
Sonnet으로 리스크 분석 + 체크리스트 생성.
"""

import os
import json
import anthropic
from app.models.idea import StartupIdea


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANALYSIS_MODEL = "claude-sonnet-4-5-20250929"


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def build_analysis_prompt(idea: StartupIdea, matched_cases: list[dict]) -> str:
    """리스크 분석을 위한 프롬프트 생성."""

    cases_text = ""
    for mc in matched_cases:
        cases_text += f"- {mc['company_name']} (유사도: {mc['similarity']}%): {mc['key_lesson']}\n"

    return f"""당신은 스타트업 실패 분석 전문가입니다. 아래 스타트업 아이디어에 대해 리스크를 분석해주세요.

## 스타트업 아이디어
- 이름: {idea.name}
- 산업: {idea.industry}
- 설명: {idea.description or '없음'}
- 단계: {idea.stage or '미정'}
- 수익 모델: {idea.revenue_model or '미정'}
- 팀 규모: {idea.team_size or '미정'}명
- 기술 공동창업자: {idea.has_technical_cofounder or '미정'}
- 팀 경험: {idea.team_experience or '미정'}
- 월간 번레이트: ${idea.monthly_burn or 0:,.0f}
- 남은 런웨이: {idea.runway_months or '미정'}개월
- 수익 발생 여부: {idea.has_revenue or '미정'}
- 목표 시장: {idea.target_market or '미정'}

## 유사한 실패 사례
{cases_text if cases_text else '매칭된 사례 없음'}

## 요청 사항
아래 JSON 형식으로 응답해주세요. JSON만 반환하고 다른 텍스트는 포함하지 마세요.

{{
  "risk_scores": {{
    "overall": <0-100>,
    "pmf": <0-100>,
    "financial": <0-100>,
    "team": <0-100>,
    "market": <0-100>,
    "timing": <0-100>,
    "competition": <0-100>,
    "execution": <0-100>
  }},
  "executive_summary": "<3-5문장 총평>",
  "threats": ["<위협1>", "<위협2>", "<위협3>"],
  "opportunities": ["<기회1>", "<기회2>", "<기회3>"],
  "timeline_predictions": [
    {{"month": <3|6|9|12|18>, "event": "<예측 이벤트>", "risk_level": "<low|medium|high|critical>", "confidence": <0.0-1.0>}}
  ],
  "checklist": [
    {{"action": "<구체적 행동>", "reason": "<이유>", "priority": "<critical|high|medium|low>", "category": "<financial|team|product|market|legal|operations>"}}
  ]
}}

리스크 점수 기준:
- 0-30: 낮은 리스크 (잘 관리되고 있음)
- 31-50: 보통 리스크 (주의 필요)
- 51-70: 높은 리스크 (즉시 조치 필요)
- 71-100: 매우 높은 리스크 (생존 위협)

체크리스트는 최소 5개, 최대 10개를 구체적이고 실행 가능한 항목으로 작성해주세요.
타임라인 예측은 향후 18개월 내 3-5개 주요 이벤트를 예측해주세요."""


def analyze_idea(idea: StartupIdea, matched_cases: list[dict]) -> dict:
    """Claude API로 아이디어 리스크 분석 (동기식)."""
    client = get_client()
    prompt = build_analysis_prompt(idea, matched_cases)

    message = client.messages.create(
        model=ANALYSIS_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    # JSON 파싱
    response_text = message.content[0].text.strip()

    # JSON 블록 추출 (```json ... ``` 가능성)
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        json_lines = []
        in_json = False
        for line in lines:
            if line.startswith("```") and not in_json:
                in_json = True
                continue
            elif line.startswith("```") and in_json:
                break
            elif in_json:
                json_lines.append(line)
        response_text = "\n".join(json_lines)

    return json.loads(response_text)


def analyze_idea_streaming(idea: StartupIdea, matched_cases: list[dict]):
    """Claude API 스트리밍 응답 제너레이터."""
    client = get_client()
    prompt = build_analysis_prompt(idea, matched_cases)

    with client.messages.stream(
        model=ANALYSIS_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
