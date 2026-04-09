# Structure

> Generated: 2026-04-09 | Project: ShortFlow (shortping-gen)

---

## Directory Layout

```
shortping-gen/
├── .claude/
│   ├── CLAUDE.md                              # 프로젝트 지침 (Claude Code 개발 가이드)
│   ├── settings.json                          # Claude Code 권한 설정 (공유)
│   ├── settings.local.json                    # Claude Code 권한 설정 (로컬)
│   ├── skills/                                # 에이전트 스킬 정의
│   │   ├── shorts-pd/SKILL.md                 # 메인 오케스트레이터
│   │   ├── trend-researcher/SKILL.md          # 트렌드 제품 발굴
│   │   ├── reference-analyzer/SKILL.md        # 레퍼런스 영상 분석
│   │   ├── script-writer/SKILL.md             # 대본 작성
│   │   ├── source-collector/SKILL.md          # 소스 수집 가이드
│   │   ├── edit-guide/SKILL.md                # CapCut 편집 가이드
│   │   └── upload-manager/SKILL.md            # 업로드 정보 생성
│   └── workspace/                             # 영상 프로젝트 작업 폴더 (비어 있음)
└── .planning/                                 # GSD 계획 문서 (자동 생성)
    └── codebase/                              # 코드베이스 분석 문서
```

---

## Key Locations

| 경로 | 용도 |
|------|------|
| `.claude/CLAUDE.md` | 프로젝트 전체 지침, 에이전트 역할 분담표, 비용 구조 |
| `.claude/skills/` | 7개 에이전트 스킬 정의 (각 SKILL.md) |
| `.claude/settings.json` | 공유 권한: Next.js, Python 관련 Bash 허용 |
| `.claude/settings.local.json` | 로컬 권한: git, curl, npm, WebFetch 등 허용 |
| `.claude/workspace/` | 영상 프로젝트별 작업 폴더 (런타임 생성) |

---

## File Types

| 확장자 | 수량 | 역할 |
|--------|------|------|
| `.md` | 8개 | SKILL 정의 (7) + CLAUDE.md (1) |
| `.json` | 2개 | Claude Code 설정 (settings.json, settings.local.json) |

**총 파일 수**: 10개 (전통적 소스 코드 없음)

---

## Naming Conventions

### 스킬 디렉토리
- **kebab-case**: `shorts-pd`, `trend-researcher`, `reference-analyzer`
- 1 스킬 = 1 디렉토리 = 1 SKILL.md

### 워크스페이스 산출물
- **번호 프리픽스**: `01_products.md`, `02_reference.md`, ..., `05_edit_guide.md`
- **한글 파일명**: `업로드_정보.md` (마지막 산출물)
- **폴더명**: `{YYYY-MM-DD}_{제품명약칭}` (예: `2026-04-09_자석청소기`)

### 설정 파일
- `settings.json`: 공유 설정 (git 추적)
- `settings.local.json`: 로컬 전용 설정 (git 제외 권장)

---

## Module Boundaries

각 스킬은 독립적이며 직접 호출하지 않음.
`shorts-pd`가 유일한 오케스트레이터로 다른 스킬을 순차 호출.

```
shorts-pd ──→ trend-researcher (독립)
          ──→ reference-analyzer (01_products.md 의존)
          ──→ script-writer (01 + 02 의존)
          ──→ source-collector (03 의존)
          ──→ edit-guide (03 + 04 의존)
          ──→ upload-manager (01 + 03 의존)
```
