---
name: shorts-pd
description: >
  숏핑 쇼츠 영상 제작 전체 워크플로우를 오케스트레이션하는 메인 PD 에이전트.
  "영상 만들어줘", "숏츠 제작", "새 영상 시작" 등의 요청 시 반드시 이 스킬을 사용한다.
  서브 에이전트들에게 작업을 위임하고 MD 파일로 컨텍스트를 전달한다.
  TTS 음성, SRT 자막, 썸네일 이미지는 자동 생성된다.
---

# 숏핑 PD — 메인 오케스트레이터

## 역할

숏핑 유튜브 쇼츠 영상 제작의 전체 워크플로우를 지휘한다.
각 단계의 실무는 전문 서브 에이전트에게 위임하고, MD 파일로 컨텍스트를 전달하며, 진행 상황을 추적한다.
**TTS 음성 / SRT 자막 / 썸네일 이미지는 Python 스크립트로 자동 생성된다** — 수동 작업 불필요.

---

## 워크플로우 개요

```
사용자 요청
    ↓
[Step 1] trend-researcher      → workspace/{날짜}_{제품}/01_products.md
    ↓ (사용자: 제품 선택)
[Step 2] reference-analyzer    → workspace/{날짜}_{제품}/02_reference.md
    ↓
[Step 3] script-writer         → workspace/{날짜}_{제품}/03_script.md
    ↓ (사용자: 대본 검토)
[Step 4] tts-generator  ⚙️자동 → audio/*.mp3 + subtitle.srt
    ↓
[Step 5] source-collector      → workspace/{날짜}_{제품}/04_sources.md
    ↓
[Step 6] edit-guide            → workspace/{날짜}_{제품}/05_edit_guide.md
    ↓
[Step 7] upload-manager        → workspace/{날짜}_{제품}/업로드_정보.md
    ↓
[Step 8] thumbnail-maker ⚙️자동 → thumbnail.png
    ↓
사용자 최종 확인 → CapCut 편집 → YouTube 업로드
```

> ⚙️ **자동 단계(Step 4, Step 8)는 사용자 확인 없이 자동 실행된다.**
> Step 4는 대본 확정 직후, Step 8은 업로드 정보 생성 직후 바로 실행.

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
/make-video 3   → tts-generator(자동)만 실행
/make-video 5   → source-collector만 실행
/make-video 8   → thumbnail-maker(자동)만 실행
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

**⚠️ 출력 형식 필수**: `[시간] 구간명` + `"나레이션"` 형식 (tts_generate.py 파서 호환).
테이블 형식으로 작성하면 Step 4(TTS 자동 생성) 파싱 실패.

대본 완성 후 사용자에게 검토 요청. 수정 사항 반영 후 다음 단계 진행.

### Step 4: TTS + SRT 자동 생성 (tts-generator) ⚙️

```
서브 에이전트 호출: tts-generator  (또는 직접 Bash로 스크립트 실행)
컨텍스트 전달: 03_script.md
출력:
  - workspace/{폴더}/audio/*.mp3 (컷별 음성)
  - workspace/{폴더}/subtitle.srt (4~9자 짧은 구절 자막)
```

실행 명령:
```bash
python3 tts_generate.py "workspace/{폴더}"
python3 split_srt.py "workspace/{폴더}"
```

> 사용자 확인 없이 자동 실행. 결과 요약만 보고.

### Step 5: 영상 소스 준비 (source-collector)

```
서브 에이전트 호출: source-collector
컨텍스트 전달: 03_script.md
출력: workspace/{폴더}/04_sources.md
```

각 컷별 이미지/영상 프롬프트 및 수집 가이드 생성.
AI 이미지 프롬프트 + 이미지→영상 변환 프롬프트 한 쌍으로 작성.

### Step 6: 편집 가이드 (edit-guide)

```
서브 에이전트 호출: edit-guide
컨텍스트 전달: 03_script.md + 04_sources.md + subtitle.srt
출력: workspace/{폴더}/05_edit_guide.md
```

CapCut 타임라인 가이드 및 체크리스트 생성.
**편집 시 `audio/*.mp3`와 `subtitle.srt`를 CapCut에 드래그하면 싱크 자동 배치됨.**

### Step 7: 업로드 정보 (upload-manager)

```
서브 에이전트 호출: upload-manager
컨텍스트 전달: 03_script.md + 01_products.md
출력: workspace/{폴더}/업로드_정보.md
```

제목 후보 3개, 설명란 + 해시태그(정확히 5개), 썸네일 문구 3줄, 쿠팡 파트너스 링크 안내 생성.

### Step 8: 썸네일 자동 생성 (thumbnail-maker) ⚙️

```
서브 에이전트 호출: thumbnail-maker (또는 직접 Bash로 스크립트 실행)
컨텍스트 전달: 업로드_정보.md + product_images/*.jpg
출력: workspace/{폴더}/thumbnail.png
```

실행 명령:
```bash
python3 thumbnail_generate.py "workspace/{폴더}"
```

> 사용자 확인 없이 자동 실행. `product_images/` 폴더에 제품 이미지가 있어야 함 (없으면 안내 후 스킵).

---

## 워크스페이스 폴더 구조

```
workspace/
└── {YYYY-MM-DD}_{제품명약칭}/
    ├── 01_products.md      # 트렌드 제품 리서치
    ├── 02_reference.md     # 레퍼런스 분석
    ├── 03_script.md        # 최종 대본 ([시간] 구간 형식 필수)
    ├── 04_sources.md       # 영상 소스 수집 가이드
    ├── 05_edit_guide.md    # CapCut 편집 타임라인 가이드
    ├── 업로드_정보.md       # 제목/해시태그/썸네일 문구/링크
    ├── audio/              # ⚙️자동: 컷별 TTS mp3
    │   ├── 01_컷_1_...mp3
    │   └── ...
    ├── subtitle.srt        # ⚙️자동: 4~9자 짧은 구절 자막
    ├── thumbnail.png       # ⚙️자동: 1080x1920 썸네일
    ├── product_images/     # 수동: 썸네일용 제품 이미지
    ├── sources/            # 수동: AI 이미지/영상/촬영 소스
    └── final/              # 수동: 완성 영상
```

---

## 사용자 개입 시점

PD가 자율 진행하되 아래 시점에만 사용자 확인 요청:

| 시점 | 이유 |
|------|------|
| Step 1 완료 후 | 제작할 제품 최종 선택 |
| Step 3 완료 후 | 대본 검토 및 수정 |
| Step 7 완료 후 | 전체 패키지 확인 |

**Step 4(TTS 자동), Step 8(썸네일 자동)은 사용자 확인 없이 자동 실행되고 결과만 보고한다.**

---

## 비용 구조 (참고)

| 항목 | 비용 | 비고 |
|------|------|------|
| Claude (대본/분석/가이드) | **₩0** | Max 플랜 포함 |
| Typecast TTS (자동) | 영상당 약 ₩500~1,000 | 글자수 기준 |
| SRT 자막 분할 (자동) | **₩0** | 로컬 파이썬 스크립트 |
| 썸네일 생성 (자동) | **₩0** | 로컬 파이썬 스크립트 (PIL) |
| 이미지 생성 (Whisk AI) | **₩0** | Google 무료 |
| 영상 생성 (선택) | 변동 | Runway/Pika 등 |
| **합계** | **약 ₩500~1,500** | API 대비 대폭 절감 |

---

## 의존 스크립트

프로젝트 루트에 위치:
- `tts_generate.py` — Typecast TTS + SRT 생성 (Step 4)
- `split_srt.py` — SRT 짧은 구절 분할 (Step 4)
- `thumbnail_generate.py` — 썸네일 생성 (Step 8)

필수 환경변수 (`.env`):
- `TYPEAI_API_KEY` — Typecast API 키

---

## 에러 복구

| 단계 | 에러 | 조치 |
|------|------|------|
| Step 4 | "TYPEAI_API_KEY 없음" | `.env`에 API 키 추가 후 재시도 |
| Step 4 | "대본 파싱 실패" | Step 3 대본이 `[시간]` 형식인지 확인, 재작성 |
| Step 8 | "제품 이미지 없음" | `product_images/`에 이미지 넣고 수동 실행 |
| Step 8 | "썸네일 문구 없음" | `업로드_정보.md`의 "🖼 썸네일 문구" 섹션 확인 |
