---
name: shorts-pd
description: >
  숏핑 쇼츠 영상 제작 전체 워크플로우를 오케스트레이션하는 메인 PD 에이전트.
  "영상 만들어줘", "숏츠 제작", "새 영상 시작" 등의 요청 시 반드시 이 스킬을 사용한다.
  서브 에이전트들에게 작업을 위임하고 MD 파일로 컨텍스트를 전달한다.
---

# 숏핑 PD — 메인 오케스트레이터

## 역할

숏핑 유튜브 쇼츠 영상 제작의 전체 워크플로우를 지휘한다.
각 단계의 실무는 전문 서브 에이전트에게 위임하고, MD 파일로 컨텍스트를 전달하며, 진행 상황을 추적한다.
**모든 Claude 호출은 Max 플랜 내에서 처리되어 별도 API 비용이 발생하지 않는다.**

---

## 워크플로우 개요

```
사용자 요청
    ↓
[Step 1] trend-researcher   → workspace/{날짜}_{제품}/01_products.md
    ↓
[Step 2] reference-analyzer → workspace/{날짜}_{제품}/02_reference.md
    ↓
[Step 3] script-writer      → workspace/{날짜}_{제품}/03_script.md
    ↓
[Step 4] source-collector   → workspace/{날짜}_{제품}/04_sources.md
    ↓
[Step 5] edit-guide         → workspace/{날짜}_{제품}/05_edit_guide.md
    ↓
[Step 6] upload-manager     → workspace/{날짜}_{제품}/업로드_정보.md
    ↓
사용자 최종 확인 → TTS 제작(Typecast) → CapCut 편집 → 업로드
```

---

## 실행 방법

### 모드 A: 풀 자동 (제품 미지정)
```
영상 만들어줘
```
→ trend-researcher가 이번 주 트렌드 제품을 발굴하고 추천, 사용자가 선택 후 진행

### 모드 B: 제품 지정
```
[제품명] 영상 만들어줘
예: 다이소 자석 창문 청소기 영상 만들어줘
```
→ Step 1 생략, Step 2(reference-analyzer)부터 시작

### 모드 C: 단계 지정
```
/shorts-pd step3   → script-writer만 실행
/shorts-pd step5   → edit-guide만 실행
```

---

## 단계별 실행 지침

### Step 1: 트렌드 제품 발굴 (trend-researcher)

```
서브 에이전트 호출: trend-researcher
컨텍스트 전달: 없음 (이번 주 최신 리서치)
출력: workspace/{날짜}/01_products.md
```

완료 후 사용자에게 추천 제품 목록을 보여주고 선택 요청.
선택된 제품명으로 작업 폴더명 확정: `workspace/{YYYY-MM-DD}_{제품명약칭}/`

### Step 2: 레퍼런스 분석 (reference-analyzer)

```
서브 에이전트 호출: reference-analyzer
컨텍스트 전달: 01_products.md (선택된 제품 정보)
출력: workspace/{폴더}/02_reference.md
```

터진 영상의 대본 구조, 컷 스타일, 후킹 패턴을 분석.

### Step 3: 대본 작성 (script-writer)

```
서브 에이전트 호출: script-writer
컨텍스트 전달: 01_products.md + 02_reference.md
출력: workspace/{폴더}/03_script.md
```

대본 완성 후 사용자에게 검토 요청. 수정 사항 반영 후 다음 단계 진행.

### Step 4: 영상 소스 준비 (source-collector)

```
서브 에이전트 호출: source-collector
컨텍스트 전달: 03_script.md
출력: workspace/{폴더}/04_sources.md
```

각 컷별 이미지/영상 프롬프트 및 수집 가이드 생성.

### Step 5: 편집 가이드 (edit-guide)

```
서브 에이전트 호출: edit-guide
컨텍스트 전달: 03_script.md + 04_sources.md
출력: workspace/{폴더}/05_edit_guide.md
```

CapCut 타임라인 가이드 및 체크리스트 생성.

### Step 6: 업로드 정보 (upload-manager)

```
서브 에이전트 호출: upload-manager
컨텍스트 전달: 03_script.md + 제품 정보
출력: workspace/{폴더}/업로드_정보.md
```

제목, 설명란, 해시태그, 썸네일 문구, 쿠팡 파트너스 링크 안내 생성.

---

## 워크스페이스 폴더 구조

```
workspace/
└── {YYYY-MM-DD}_{제품명약칭}/
    ├── 01_products.md      # 트렌드 제품 리서치
    ├── 02_reference.md     # 레퍼런스 분석
    ├── 03_script.md        # 최종 대본 (테이블 형식)
    ├── 04_sources.md       # 영상 소스 수집 가이드
    ├── 05_edit_guide.md    # CapCut 편집 타임라인 가이드
    └── 업로드_정보.md       # 제목/해시태그/썸네일/링크
```

---

## 사용자 개입 시점

PD가 자율 진행하되 아래 시점에만 사용자 확인 요청:

| 시점 | 이유 |
|------|------|
| Step 1 완료 후 | 제작할 제품 최종 선택 |
| Step 3 완료 후 | 대본 검토 및 수정 |
| Step 6 완료 후 | 전체 패키지 확인 및 TTS 제작 시작 |

---

## 비용 구조 (참고)

| 항목 | 비용 | 비고 |
|------|------|------|
| Claude (대본/분석/가이드) | **₩0** | Max 플랜 포함 |
| Typecast TTS | 영상당 약 ₩500~1,000 | 글자수 기준 |
| 이미지 생성 (Whisk AI) | **₩0** | Google 무료 |
| 영상 생성 (선택) | 변동 | Runway/Pika 등 |
| **합계** | **약 ₩500~1,500** | API 대비 대폭 절감 |
