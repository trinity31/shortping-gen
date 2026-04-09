# Conventions

> Generated: 2026-04-09 | Project: ShortFlow (shortping-gen)

---

## Project Type

**Claude Code Harness** — 전통적 소스 코드가 아닌 Markdown 기반 에이전트 스킬 정의서.
코딩 컨벤션보다 **문서 작성 컨벤션**이 핵심.

---

## SKILL.md 문서 구조

모든 스킬은 동일한 구조를 따름:

```markdown
---
name: {skill-name}              # kebab-case
description: >                  # Claude Code 디스커버리용 설명
  {한국어 설명 1~3줄}
---

# {스킬 한국어 이름}

## 역할
{1~2문장 역할 설명}

## 입력
{의존하는 MD 파일 목록}

## 실행 단계
### Step 1: ...
### Step 2: ...

## 출력 파일 형식
{`workspace/{폴더}/{파일명}.md` + 마크다운 템플릿}

## 완료 후 액션
{shorts-pd에 완료 보고}
```

---

## Naming Patterns

| 대상 | 패턴 | 예시 |
|------|------|------|
| 스킬명 | kebab-case | `trend-researcher`, `script-writer` |
| 산출물 파일 | 번호_스네이크 | `01_products.md`, `03_script.md` |
| 워크스페이스 폴더 | 날짜_한글약칭 | `2026-04-09_자석청소기` |
| 변수/플레이스홀더 | 중괄호 | `{제품명}`, `{날짜}`, `{폴더}` |

---

## Content Style

- **언어**: 한국어 기본, 기술 용어는 영어 혼용
- **톤**: 명령형 / 지시형 ("~한다", "~작성한다")
- **구성**: 테이블 적극 활용, 코드 블록으로 출력 형식 예시 제공
- **정보량**: 구체적 — 초 단위 시간, 글자 수, 가격, 비율 등 수치 포함

---

## Data Format Conventions

### 산출물 헤더
```markdown
# {제목}
> {메타 정보: 제품명 | 날짜 | 기타 컨텍스트}
```

### 대본 테이블
```markdown
| 자막 (나레이션) | 영상컷 | 시간 |
|----------------|--------|------|
```

### 소스 수집 테이블
```markdown
| 컷# | 자막 | 소스 유형 | 수집 방법 |
```

### 제품 등급 분류
- **S급**: 채널 평균 조회수 3배 이상 또는 10만+
- **A급**: 채널 평균 1.5~3배 또는 3~10만
- **B급**: 평균 수준이나 트렌드 부합

---

## External Tool Conventions

| 도구 | 접근 방식 |
|------|-----------|
| YouTube 채널 분석 | JavaScript DOM 셀렉터 주입 (`querySelectorAll('a[href*="/shorts/"]')`) |
| AI 이미지 | Google Whisk — 영문 프롬프트 (`"[scene], [style], [lighting], [angle], [color]"`) |
| TTS | Typecast — 수동 접속 및 생성 |
| 편집 | CapCut — 수동 (API 없음) |
| 수익화 | 쿠팡 파트너스 — 수동 링크 생성 |

---

## Error Handling

현재 에러 핸들링 패턴이 정의되어 있지 않음.
각 SKILL.md는 정상 경로만 기술하며, 실패 시나리오에 대한 지침 없음.

---

## Documentation Patterns

- 모든 문서는 한국어
- 이모지 사용: 섹션 구분용 (📌, 📦, 🛒, 🖼, ✅)
- 체크리스트: `- [ ]` 형식으로 수동 확인 항목 표기
- 비용 정보: 원화(₩) 단위, 영상당 비용 기준
