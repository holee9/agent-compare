# Playwright Gateway Design - Proxima 대체 아키텍처

> **확정일**: 2026-02-15
> **상태**: Approved
> **영향 범위**: SPEC-PIPELINE-001 AI 게이트웨이 계층

---

## 1. 배경 및 문제

### Proxima 방식의 한계

Proxima(Electron 기반 데스크톱 앱)는 브라우저 세션 쿠키를 import하여 AI 서비스에 접근하는 방식을 사용한다.

- 쿠키만 복사하므로 서비스가 "새 기기"로 인식 → 빠르게 만료
- 복구 과정: 수동 Chrome 로그인 → Cookie-Editor 추출 → import 스크립트 실행
- 자동화 파이프라인의 근본 목적과 모순

### 제약 조건

- API 키 사용 불가 (구독형만 사용)
- 브라우저 세션 기반 접근 필수

---

## 2. 해결 방안: Playwright 영구 프로필

### 핵심 아이디어

Proxima를 제거하고, Playwright의 **persistent browser context**를 사용하여 AI 서비스에 직접 접근한다.

- 브라우저 프로필 전체(쿠키 + localStorage + sessionStorage + fingerprint)를 디스크에 저장
- 서비스가 "같은 사용자의 같은 브라우저"로 인식 → 세션 수주~수개월 유지
- 파이프라인 내부에서 직접 브라우저를 제어 (별도 프로세스 불필요)

### 아키텍처 비교

```
[기존 Proxima 방식]
CLI → HTTP 요청 → Proxima (Electron 앱, 별도 프로세스) → 내장 브라우저 → AI

[새로운 Playwright 방식]
CLI → Python 코드에서 직접 → Playwright 브라우저 → AI
                              ↑ 영구 프로필 디스크 저장
                              ↑ 파이프라인과 같은 프로세스
```

---

## 3. 사용 흐름

```
최초 설정: agent-compare setup    → 브라우저 창 열림 → 각 AI에 로그인 → 프로필 저장
일반 사용: agent-compare run ...  → 저장된 프로필로 headless 실행 → 자동 동작
세션 만료: agent-compare relogin  → 만료된 서비스만 브라우저 창 열림 → 재로그인
```

---

## 4. 세션 자동 복구 체인

AI 요청 실패 시 4단계 복구 체인을 실행한다.

```
AI에 요청 시도
    │
    ├─ 성공 → 정상 진행
    │
    └─ 실패 (세션 만료 감지)
         │
         ├─ Level 1: 세션 자동 갱신 (페이지 리로드, 쿠키 리프레시)
         │    ├─ 성공 → 정상 진행
         │    └─ 실패 ↓
         │
         ├─ Level 2: 브라우저 창 팝업 → 사용자 수동 재로그인
         │    ├─ 파이프라인 일시정지 (타임아웃 2분)
         │    ├─ 성공 → 프로필 저장 후 재개
         │    └─ 실패/타임아웃 ↓
         │
         ├─ Level 3: 대체 AI로 폴백
         │    ├─ ChatGPT ↔ Claude (지정 폴백 쌍)
         │    ├─ Gemini ↔ Perplexity (지정 폴백 쌍)
         │    ├─ 성공 → 폴백 AI로 계속 진행
         │    └─ 실패 ↓
         │
         └─ Level 4: Claude 최종 안전망
              ├─ 모든 Phase에서 Claude로 대체 시도
              └─ Claude도 실패 시 → 파이프라인 상태 저장 후 중단
```

### Phase별 폴백 매핑

| Phase | 메인 AI | 지정 폴백 | 최종 안전망 |
|:---:|:---:|:---:|:---:|
| 1 | ChatGPT | Claude | - (이미 Claude) |
| 2 | Gemini | Perplexity | Claude |
| 3 | ChatGPT | Claude | - (이미 Claude) |
| 4 | Claude | ChatGPT | - (이미 Claude) |
| 5 | Perplexity | Claude | - (이미 Claude) |

---

## 5. Provider Adapter 설계

### 구조

```
BaseProvider (공통 인터페이스)
  ├── send_message(prompt) → response
  ├── check_session() → bool
  ├── login_flow() → 브라우저 창 팝업
  └── detect_response() → 응답 텍스트 추출

    ▼ 상속

ChatGPTProvider    → chat.openai.com DOM 제어
ClaudeProvider     → claude.ai DOM 제어
GeminiProvider     → gemini.google.com DOM 제어
PerplexityProvider → perplexity.ai DOM 제어
```

### 각 어댑터 담당

- 서비스별 URL, 입력창/전송 버튼 셀렉터
- 응답 완료 감지 (스트리밍 종료 시점)
- 세션 만료 감지 (로그인 페이지 리다이렉트 등)
- 서비스별 특이사항 처리

### DOM 변경 대응

셀렉터를 외부 설정 파일(`~/.agent-compare/selectors.yaml`)로 분리하여 코드 수정 없이 업데이트 가능.

---

## 6. 프로필 저장 구조

```
~/.agent-compare/
  profiles/
    chatgpt/       ← Playwright persistent context
    claude/
    gemini/
    perplexity/
  selectors.yaml   ← DOM 셀렉터 설정 (외부 업데이트 가능)
  sessions.json    ← 마지막 헬스체크 시간, 상태 기록
```

---

## 7. SPEC 변경 영향

### 변경되는 부분

| 항목 | 기존 (Proxima) | 변경 (Playwright) |
|------|---------------|-------------------|
| AI 게이트웨이 | Proxima Electron 앱 (별도 프로세스) | Playwright 내장 (파이프라인 내부) |
| 의존성 | aiohttp → localhost:3210 | playwright-python → 직접 브라우저 제어 |
| 세션 관리 | 수동 쿠키 import | 영구 프로필 + 자동 복구 체인 |
| 시스템 요구사항 | Proxima 사전 설치 필요 | Playwright 브라우저 자동 설치 |
| 폴백 | 2단계 (메인 → 지정 폴백) | 4단계 (메인 → 복구 → 지정폴백 → Claude → 중단) |
| 출력 포맷 | OpenAI 호환 JSON | 자체 응답 객체 (내부용) |

### 변경되지 않는 부분

- 5단계 파이프라인 구조
- AI별 역할 배치
- 컨텍스트 체인, 상태 저장/재개
- CLI 인터페이스
- --type 모드 분기 (bizplan/rd)
- Jinja2 템플릿 시스템

---

## 8. 기술 의존성 변경

| 제거 | 추가 |
|------|------|
| aiohttp | playwright (async) |
| Proxima v3.0.0 (외부 앱) | playwright install chromium |

---

**최종 업데이트**: 2026-02-15
