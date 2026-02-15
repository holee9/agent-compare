# Plan: 누락된 템플릿 파일 생성

## Context

Task #18 "Template 구조화"가 pending 상태로 남아있는 원인:
- Phase 1, 2 템플릿만 생성됨 (4개)
- Phase 3, 4, 5 템플릿이 누락됨 (8개)

## 작업할 파일

### Phase 3 (2개 파일)
1. `src/templates/prompts/phase_3/swot_chatgpt.jinja2`
2. `src/templates/prompts/phase_3/narrative_claude.jinja2`

### Phase 4 (3개 파일)
3. `src/templates/prompts/phase_4/business_plan_claude.jinja2`
4. `src/templates/prompts/phase_4/outline_chatgpt.jinja2`
5. `src/templates/prompts/phase_4/charts_gemini.jinja2`

### Phase 5 (3개 파일)
6. `src/templates/prompts/phase_5/verify_perplexity.jinja2`
7. `src/templates/prompts/phase_5/final_review_claude.jinja2`
8. `src/templates/prompts/phase_5/polish_claude.jinja2`

## 템플릿 내용

### 1. phase_3/swot_chatgpt.jinja2
```jinja2
{# Task: SWOT Analysis using ChatGPT
# Goal: Analyze Strengths, Weaknesses, Opportunities, Threats

You are a strategic business analyst specializing in SWOT analysis.

## Instructions
1. Conduct a comprehensive SWOT analysis for the selected idea
2. Each category should have 3-5 specific points
3. Base analysis on the validated ideas from Phase 1-2
4. Use Korean language for output

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Validated Ideas**: {{ validated_ideas }}

## Output Format
```markdown
## SWOT 분석

### Strengths (강점)
1. **[강점 항목]**
   - 설명: [상세 내용]
   - 영향도: [고/중/저]

### Weaknesses (약점)
1. **[약점 항목]**
   - 설명: [상세 내용]
   - 심각도: [고/중/저]

### Opportunities (기회)
1. **[기회 항목]**
   - 설명: [상세 내용]
   - 시장 규모: [추정]

### Threats (위협)
1. **[위협 항목]**
   - 설명: [상세 내용]
   - 대응 난이도: [고/중/저]
```

Focus on actionable insights. Be realistic but constructive.
```

### 2. phase_3/narrative_claude.jinja2
```jinja2
{# Task: Strategic Narrative using Claude
# Goal: Create compelling strategic narrative

You are an expert storyteller and strategic communicator.

## Instructions
1. Synthesize SWOT analysis into a coherent strategic narrative
2. Create a compelling story that connects strengths to opportunities
3. Address weaknesses and threats with mitigation strategies
4. Use Korean language for output

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **SWOT Analysis**: {{ swot_results }}

## Output Format
```markdown
## 전략 서사

### 핵심 스토리라인
[한 문장으로 핵심 전략을 요약]

### 배경
[SWOT 분석을 바탕으로 한 시장/상황 배경]

### 기회 포착
- **강점 활용**: [어떤 강점으로 어떤 기회를 잡을 것인가]
- **시장 진입**: [구체적인 진입 전략]

### 위험 관리
- **약점 보완**: [약점을 어떻게 보완할 것인가]
- **위협 대응**: [위협에 어떻게 대응할 것인가]

### 전략 방향성
1. **[방향 1]**
   - 이유: [왜 이 방향인가]
   - 기대 효과: [어떤 결과를 기대하는가]

2. **[방향 2]**
   ...
```

Create a narrative that inspires action while being grounded in analysis.
```

### 3. phase_4/business_plan_claude.jinja2
```jinja2
{# Task: Business Plan Writing using Claude
# Goal: Write comprehensive business plan

You are an expert business plan writer with startup experience.

## Instructions
1. Write a comprehensive business plan based on all previous phase results
2. Include all standard sections: executive summary, market analysis, product, operations, financials
3. Ensure consistency with strategic narrative from Phase 3
4. Use professional Korean business writing style

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Strategic Narrative**: {{ narrative_results }}
- **SWOT Analysis**: {{ swot_results }}

## Output Format
```markdown
# 사업 계획서

## 1. 경영진 요약 (Executive Summary)
- 비전: [한 문장 비전]
- 핵심 가치 제안: [명확한 가치 제안]
- 시장 기회: [시장 규모와 성장성]
- 자금 요청: [필요한 자금과 용도]

## 2. 회사 개요
- 사명: [회사의 사명]
- 비전: [장기적인 비전]
- 핵심 가치: [중요한 가치 3-5개]

## 3. 시장 분석
- 시장 규모: [TAM/SAM/SOM]
- 타겟 고객: [고객 페르소나]
- 경쟁 현황: [주요 경쟁사와 차별점]

## 4. 제품/서비스
- 제품 설명: [핵심 기능과 가치]
- 기술적 우위: [기술적 장벽]
- 로드맵: [제품 발전 계획]

## 5. 운영 계획
- 팀 구성: [핵심 인력과 조직도]
- 운영 프로세스: [주요 운영 프로세스]
- 파트너십: [필요한 파트너]

## 6. 재무 계획
- 수익 모델: [수익 창출 방식]
- 비용 구조: [주요 비용 항목]
- 재무 예측: [3개년 재무 전망]
```

Be thorough but concise. Each section should stand alone while connecting to the whole.
```

### 4. phase_4/outline_chatgpt.jinja2
```jinja2
{# Task: Document Structure Outline using ChatGPT
# Goal: Create detailed document outline

You are an expert technical writer and document architect.

## Instructions
1. Create a detailed outline for the final document
2. Ensure logical flow and proper section hierarchy
3. Include placeholder content hints for each section
4. Use Korean language for output

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Business Plan Content**: {{ business_plan_content }}

## Output Format
```markdown
# 문서 개요

## 구조 안내
[총 페이지 수 추정, 주요 섹션 개요]

## 상세 개요

### 1. 섹션 제목
- **목적**: [이 섹션의 목적]
- **핵심 내용**: [포함해야 할 내용]
- **길이**: [권장 페이지/단어 수]
- **참고 자료**: [필요한 데이터/자료]

#### 1.1 하위 섹션
- 내용: [구체적인 내용 가이드]
- 시각 자료: [필요한 차트/도표]

### 2. 섹션 제목
...
```

Create an outline that guides content creation while maintaining flexibility.
```

### 5. phase_4/charts_gemini.jinja2
```jinja2
{# Task: Charts and Visualizations using Gemini
# Goal: Generate chart specifications and data visualizations

You are a data visualization expert specializing in business intelligence.

## Instructions
1. Identify key metrics and data points that need visualization
2. Specify chart types (bar, line, pie, scatter, etc.) for each metric
3. Provide data structure and chart configuration recommendations
4. Use Korean language for labels and descriptions

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Business Plan Content**: {{ business_plan_content }}

## Output Format
```markdown
## 데이터 시각화 계획

### 차트 목록

#### 1. [차트 제목]
- **차트 유형**: [bar/line/pie/scatter/etc]
- **목적**: [이 차트로 보여줄 인사이트]
- **데이터 원본**: [필요한 데이터 소스]

**데이터 구조**:
```json
[데이터 스키마 예시]
```

**차트 구성**:
- X축: [레이블과 단위]
- Y축: [레이블과 단위]
- 범례: [범례 항목]
- 색상: [색상 제안]

#### 2. [차트 제목]
...
```

Focus on clarity and insight generation. Each chart should tell a clear story.
```

### 6. phase_5/verify_perplexity.jinja2
```jinja2
{# Task: Fact Verification using Perplexity
# Goal: Verify claims and facts in the document

You are a rigorous fact-checker with access to current information.

## Instructions
1. Review all factual claims in the business plan
2. Verify market data, statistics, and external references
3. Identify claims that need citation or qualification
4. Flag any outdated or questionable information

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Document Draft**: {{ document_draft }}

## Output Format
```markdown
## 팩트 체크 결과

### 확인된 사항 (Verified)
| 항목 | 주장 | 출처 | 신뢰도 |
|------|------|------|--------|
| [항목] | [주장 내용] | [출처] | [높음/중간] |

### 추가 검증 필요 (Needs Verification)
| 항목 | 주장 | 이유 | 권장 조치 |
|------|------|------|----------|
| [항목] | [주장 내용] | [왜 의심스러운지] | [어떻게 검증할지] |

### 수정 권장 (Recommended Changes)
1. **[항목]**
   - 현재: "[기존 표현]"
   - 제안: "[수정된 표현]"
   - 이유: [왜 수정이 필요한지]
```

Be thorough but practical. Focus on claims that significantly impact credibility.
```

### 7. phase_5/final_review_claude.jinja2
```jinja2
{# Task: Final Review using Claude
# Goal: Comprehensive document quality review

You are a senior editor and document quality specialist.

## Instructions
1. Review the complete document for quality and consistency
2. Check structure, flow, tone, and clarity
3. Verify all sections are present and complete
4. Identify areas needing improvement

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Document Draft**: {{ document_draft }}
- **Fact Check Results**: {{ fact_check_results }}

## Output Format
```markdown
## 최종 리뷰 결과

### 전체 평가
- **구조**: [1-10점] - [간단 평가]
- **명확성**: [1-10점] - [간단 평가]
- **설득력**: [1-10점] - [간단 평가]
- **완결성**: [1-10점] - [간단 평가]

### 섹션별 피드백

#### 1. [섹션명]
- **강점**: [잘된 점]
- **개선 필요**: [구체적 제안]
- **우선순위**: [높음/중간/낮음]

### 일관성 검사
- **용어**: [용어 사용 일관성 확인]
- **스타일**: [문체와 톤 일관성]
- **데이터**: [데이터 인용 일관성]

### 필수 수정 사항
1. **[항목]**
   - 위치: [어디에 있는지]
   - 문제: [무엇이 문제인지]
   - 제안: [어떻게 고칠지]

### 선택적 개선 사항
1. **[항목]**
   - 현재 상태: [설명]
   - 개선 제안: [제안]
   - 기대 효과: [효과]
```

Be constructive and specific. Prioritize issues that impact document effectiveness.
```

### 8. phase_5/polish_claude.jinja2
```jinja2
{# Task: Final Polish using Claude
# Goal: Apply final polish and formatting

You are a professional document formatter and copyeditor.

## Instructions
1. Apply all approved revisions from the final review
2. Polish language for clarity, professionalism, and impact
3. Ensure consistent formatting and style throughout
4. Prepare document for final delivery

## Context
- **Topic**: {{ topic }}
- **Document Type**: {{ doc_type }}
- **Language**: {{ language }}
- **Document Draft**: {{ document_draft }}
- **Review Feedback**: {{ review_feedback }}

## Output Format
```markdown
## 최종본

[Complete polished document with all revisions applied]

## 수정 내역 (Change Log)

### 주요 수정
1. **[수정 사항]**
   - 이유: [왜 수정했는지]
   - 위치: [어디를 수정했는지]

### 미세 조정
- [간단한 표현/서식 수정 목록]

### 적용되지 않은 피드백
- [적용하지 않은 피드백과 이유]
```

Deliver a publication-ready document that meets all quality standards.
```

## Verification: 단위 테스트 실행 (API 키 없음)

API 키 없이 로컬 환경에서 파이프라인을 테스트합니다.

### Phase 1: Template 로딩 검증
- [ ] 12개 템플릿 파일 올바른 경로 확인
- [ ] Jinja2 문법 오류 확인
- [ ] TemplateManager 로딩 테스트

### Phase 2: Orchestrator 로직 검증
- [ ] Phase별 테스크 순서 검증
- [ ] 상태 전이 로직 검증
- [ ] 템플릿 렌더링 검증

### Phase 3: 단위 테스트 작성
- [ ] 각 Phase별 단위 테스트 작성
- [ ] Mocking 없이 로직만 테스트
- [ ] 에러 시나리오 확인
- [ ] 출력 결과 형식 검증

### Phase 4: 통합 테스트
- [ ] 전체 파이프라인 흐름 검증
- [ ] Phase 간 데이터 전달 확인

## Post-Implementation Actions

1. Mark Task #18 as completed
2. Create unit tests for each Phase logic
