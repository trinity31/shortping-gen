# Architecture

> Generated: 2026-04-09 | Project: ShortFlow (shortping-gen)

---

## Architecture Pattern

**Multi-Agent Orchestration (Claude Code Harness)**

이 프로젝트는 전통적인 소스 코드 기반이 아닌 **Claude Code 스킬 기반 에이전트 오케스트레이션** 패턴이다.
런타임 코드가 없으며, 모든 로직은 SKILL.md (Markdown + YAML frontmatter) 파일에 선언적으로 정의된다.

---

## System Layers

```
┌─────────────────────────────────────────────┐
│  Layer 1: Orchestration                      │
│  shorts-pd (메인 PD)                         │
│  → 전체 워크플로우 지휘, 서브 에이전트 위임   │
├─────────────────────────────────────────────┤
│  Layer 2: Research                           │
│  trend-researcher → reference-analyzer       │
│  → 트렌드 발굴 → 레퍼런스 패턴 분석          │
├─────────────────────────────────────────────┤
│  Layer 3: Content Creation                   │
│  script-writer → source-collector            │
│  → 대본 작성 → 소스 수집 가이드              │
├─────────────────────────────────────────────┤
│  Layer 4: Production                         │
│  edit-guide → upload-manager                 │
│  → CapCut 편집 가이드 → 업로드 정보 생성      │
└─────────────────────────────────────────────┘
```

---

## Data Flow

```
사용자 요청
    ↓
[shorts-pd] ─── 오케스트레이터
    ↓
[trend-researcher] → 01_products.md
    ↓ (사용자 제품 선택)
[reference-analyzer] ← 01_products.md → 02_reference.md
    ↓
[script-writer] ← 01_products.md + 02_reference.md → 03_script.md
    ↓ (사용자 대본 검토)
[source-collector] ← 03_script.md → 04_sources.md
    ↓
[edit-guide] ← 03_script.md + 04_sources.md → 05_edit_guide.md
    ↓
[upload-manager] ← 03_script.md + 01_products.md → 업로드_정보.md
    ↓ (사용자 최종 확인)
사용자 수동 작업 → TTS(Typecast) → CapCut 편집 → YouTube 업로드
```

**컨텍스트 전달 방식**: 에이전트 간 MD 파일 기반 — 각 에이전트는 이전 단계 파일만 읽음 (Context Rot 방지).

---

## Key Abstractions

### 1. Agent Skill (SKILL.md)
- YAML frontmatter: `name`, `description` (Claude Code 스킬 디스커버리용)
- Markdown body: 역할, 입력, 실행 단계, 출력 형식, 완료 후 액션
- 단일 책임 원칙: 각 스킬은 정확히 하나의 워크플로우 단계만 담당

### 2. Workspace
- `workspace/{YYYY-MM-DD}_{제품명약칭}/` 패턴
- 영상 프로젝트별 독립 폴더
- 6개 아티팩트 파일로 전체 제작 과정 기록

### 3. Document Chain
- 순차적 의존성: 01 → 02 → 03 → 04 → 05 → 업로드_정보
- 각 문서는 이전 문서에 의존하지만 직전 1~2개만 읽음
- 사용자 개입 포인트 3곳 (Step 1, 3, 6 완료 후)

---

## Entry Points

| 진입점 | 트리거 | 설명 |
|--------|--------|------|
| `shorts-pd` | "영상 만들어줘" | 전체 워크플로우 시작 (모드 A: 풀 자동) |
| `shorts-pd` | "{제품명} 영상 만들어줘" | Step 2부터 시작 (모드 B: 제품 지정) |
| `shorts-pd` | "/shorts-pd stepN" | 특정 단계만 실행 (모드 C: 단계 지정) |

---

## Error Handling Strategy

현재 **명시적 에러 핸들링 없음**. 각 SKILL.md는 정상 경로(happy path)만 정의.
- 에이전트 실패 시: shorts-pd에서 재시도 또는 사용자에게 보고
- 외부 서비스 장애 시: 대안 경로 미정의
- 입력 검증: 스키마 없음 (MD 파일 구조에 암묵적 의존)

---

## Cross-Cutting Concerns

- **비용 관리**: Claude Max 플랜 무료 + TTS만 유료 (₩500~1,000/영상)
- **보안**: 쿠팡 파트너스 링크만 외부 노출, API 키 없음
- **확장성**: 에이전트 추가로 워크플로우 확장 가능 (스킬 파일 추가)
