# Multi-AI Pipeline BizPlan

4개 AI(ChatGPT, Claude, Gemini, Perplexity)를 교차 활용하여 사업계획서와 R&D 계획서를 자동 생성하는 MoAI-ADK 스킬입니다.

## 개요

단일 AI의 한계를 넘어, 각 AI의 강점을 단계별로 조합하는 멀티에이전트 파이프라인입니다.

| AI | 역할 | 강점 |
|:---:|---|---|
| **ChatGPT** | 발상가 / 프레임워크 장인 | 창의적 발산, SWOT/PESTEL 분석, 편집 |
| **Claude** | 설계자 / 집필자 | 논리적 수렴, 장문 일관성, 전문 문체 |
| **Gemini** | 리서치 군단 | Deep Research, 100+ 소스, 표/그래프 |
| **Perplexity** | 팩트 라이브러리 | 실시간 검색, 자동 인용, 팩트체크 |

## 파이프라인 구조

```
[아이디어 입력]
    │
    ▼
Phase 1: 컨셉 프레이밍
    ChatGPT(발산) → Claude(수렴/검증)
    │
    ▼
Phase 2: 심층 리서치 (병렬)
    Gemini(범위) + Perplexity(정확도) → Claude(교차검증)
    │
    ▼
Phase 3: 전략 설계
    ChatGPT(SWOT/PESTEL) → Claude(서사 통합)
    │
    ▼
Phase 4: 계획서 초안
    Claude(본문 집필) + ChatGPT(요약) + Gemini(시각자료)
    │
    ▼
Phase 5: 최종 검수
    Perplexity(팩트체크) → Claude(오류 반영)
    │
    ▼
[완성된 계획서]
```

각 Phase 사이에 사용자 검토/수정이 가능합니다.

## 아키텍처

- **마스터 스킬**: `moai-pipeline-bizplan` - `/bizplan` 커맨드로 실행
- **MCP 서버 3개**: 외부 AI를 MCP 프로토콜로 래핑
  - `mcp-openai` - ChatGPT API
  - `mcp-gemini` - Gemini API
  - `mcp-perplexity` - Perplexity API
- **상태 저장**: `.moai/pipeline/{session-id}/`에 Phase별 결과 저장

## 사용 방법

### 사전 준비

1. API 키를 환경 변수로 설정:

```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export PERPLEXITY_API_KEY="pplx-..."
```

2. MCP 서버 설치:

```bash
cd mcp-servers/mcp-openai && npm install
cd mcp-servers/mcp-gemini && npm install
cd mcp-servers/mcp-perplexity && npm install
```

### 실행

Claude Code에서:

```
/bizplan "AI 기반 헬스케어 플랫폼 사업계획서"
```

Phase별로 결과가 생성되며, 각 단계에서 검토/수정할 수 있습니다.

### 중단 후 재개

```
/bizplan resume bizplan-20260215-143022
```

### API 키 없이 사용

API 키가 설정되지 않은 AI는 Claude가 대신 처리합니다. 모든 API 키 없이도 Claude 단독으로 전체 파이프라인 실행이 가능합니다 (교차검증 이점은 감소).

## 출력물

| 파일 | 내용 |
|------|------|
| `phase1-concept.md` | 컨셉 프레이밍 (BM 캔버스, 후보 분석) |
| `phase2-research.md` | 심층 리서치 (시장/기술/경쟁사/규제) |
| `phase3-strategy.md` | 전략 설계 (SWOT, PESTEL, 재무, KPI) |
| `phase4-draft.md` | 계획서 초안 (본문 + 요약 + 시각자료) |
| `final-bizplan.md` | 팩트체크 완료된 최종 계획서 |

## 프로젝트 구조

```
agent-compare/
├── proxima/                   # Proxima Multi-AI 게이트웨이 (서브모듈)
├── docs/
│   ├── plans/                 # 설계 문서
│   └── guides/                # API 키 발급 가이드
├── .claude/skills/moai-pipeline-bizplan/
│   └── SKILL.md               # 마스터 스킬 정의
├── final-summary.md           # 4개 AI 교차검증 최종안
└── .moai/pipeline/            # 파이프라인 실행 상태
```

## 검증 기록 (2026-02-15)

### API 키 인증 검증

| 서비스 | 인증 | 실제 호출 | 비고 |
|--------|:----:|:--------:|------|
| OpenAI | O | X | 키 유효하나 크레딧 없음 (`insufficient_quota`) |
| Gemini | O | X | 키 유효하나 무료 일일 한도 소진 (`limit: 0`) |
| Perplexity | O | O | Pro 세션 토큰 유효 (만료: 2026-03-16) |

### 웹 세션 기반 MCP 검증 (Proxima)

[Proxima](https://github.com/Zen4-bit/Proxima)를 통해 웹 구독(ChatGPT Plus, Gemini, Perplexity Pro) 세션을 MCP로 래핑하여 테스트했습니다.

**단순 테스트 (1+1)**:

| AI | 결과 | 응답 시간 |
|:---:|:----:|:--------:|
| Perplexity | O 정상 | 9초 |
| ChatGPT | O 정상 | 49초 |
| Gemini | X 캡처 실패 | 24초 |

**리서치 질문 교차검증 테스트** ("2026년 한국 AI 헬스케어 시장 규모와 주요 기업"):

| AI | 결과 | 문제점 |
|:---:|:----:|--------|
| Perplexity | 부분 성공 | 질문 주제와 다소 다른 일반 AI 트렌드 응답 |
| ChatGPT | 실패 | 기존 대화 맥락 오염으로 완전히 다른 주제 응답 |
| Gemini | 실패 | 응답 캡처 불가 ("No response captured") |

### 교차검증 유효성 분석

**의미 있는 교차검증**:
- 검색 AI(Perplexity/Gemini) vs 생성 AI(Claude/ChatGPT): 정보 소스가 근본적으로 다름
- Gemini DR vs Perplexity: 검색 방법론 차이 (범위 vs 정확도)

**의미 약한 교차검증**:
- ChatGPT vs Claude: 유사한 학습 데이터, 비슷한 편향과 실패 모드
- LLM이 다른 LLM의 논리를 검증하는 것: 효과 제한적

### 연동 방식별 비교

| 방식 | 비용 | 안정성 | 자동화 적합성 |
|------|:----:|:------:|:------------:|
| API 직접 호출 (유료) | 높음 | 높음 | 높음 |
| 웹 세션 MCP (Proxima) | 무료 | 낮음 | 낮음 |
| Claude + WebSearch | 포함 | 높음 | 높음 |

### 현실적 결론

1. **웹 세션 방식은 자동화 파이프라인에 부적합**: 대화 맥락 오염, 응답 캡처 실패, 세션 만료 등 안정성 문제
2. **API 방식은 비용 필요**: OpenAI 최소 $5, Perplexity $5 크레딧 충전 필요
3. **즉시 사용 가능한 조합**: Claude + WebSearch만으로 핵심 가치(생성 + 팩트체크) 구현 가능
4. **외부 AI는 점진적 추가 권장**: API 크레딧 확보 후 실질적 가치가 있는 검색 AI(Perplexity/Gemini)부터 연동

## 교차검증 근거

이 파이프라인 설계는 Claude, ChatGPT, Gemini, Perplexity 4개 AI에게 각각 최적의 워크플로우를 물어본 뒤 교차 대조하여 확정한 것입니다. 자세한 내용은 [`final-summary.md`](./final-summary.md)를 참조하세요.

## 라이선스

Apache-2.0
