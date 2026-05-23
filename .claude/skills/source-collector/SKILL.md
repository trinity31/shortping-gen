---
name: source-collector
description: >
  대본의 각 컷에 맞는 이미지/영상 소스 수집 가이드를 작성하는 에이전트.
  AI 이미지 생성 프롬프트와 실제 촬영/수집 가이드를 제공한다.
---

# 소스 수집 가이드

## 역할

03_script.md의 각 컷 설명을 분석하여 실제 소스를 어떻게 구할지 안내한다.
AI 이미지 생성 프롬프트, 쿠팡/네이버 제품 이미지 활용 방법, 직접 촬영 가이드를 포함한다.
AI영상을 생성할 필요가 있는 경우 higgsfield-ai 스킬을 사용해서 직접 영상을 생성한다. 영상 생성시에는 사용자의 승인 후 진행한다. 

---

## 입력

- `workspace/{폴더}/03_script.md` — 최종 대본 (컷 설명 포함)

---

## 소스 유형 분류

| 유형 | 도구 | 비용 | 용도 |
|------|------|------|------|
| AI 이미지 | Google Whisk AI | 무료 | 정지 이미지 생성 (영상 변환 전 단계) |
| **AI 영상 (메인 권장)** | **`higgsfield-generate` 스킬** ⭐ | 크레딧/클립 | Seedance 2.0 / Nano Banana / Kling 3.0 등 모델 자동 선택. **반드시 사용자 승인 후 호출** |
| AI 영상 (실사·제품 일관) | Seedance 2.0 (higgsfield 내장 기본) | $0.30/클립 | 제품 + 인물 + 환경 일관, References 시스템 |
| **🆕 AI 영상 (10초 / Multi-modal / V2V 편집)** | **Gemini Omni Flash** | Google AI Studio 플랜 | 최대 10초 클립, Multi-modal References, Video-to-Video 텍스트 편집, Recurring Cast 캐릭터 일관성 |
| AI 영상 (실사) | Google Veo 3.1 | 무료 | higgsfield 미사용 시 대안 |
| AI 영상 (모션) | CapCut 내장 AI | 무료 | 제품/정물 단순 모션 |
| 제품 이미지 | 쿠팡/네이버 스토어 캡처 | 무료 (저작권 확인) | 제품 패키지, 리뷰 캡처 |
| 직접 촬영 | 스마트폰 | 무료 | 실제 사용 시연, 표정 |

---

## 🚨 AI 영상 생성 절차 (필수 준수)

AI 영상이 필요한 컷은 다음 절차로 진행:

1. **04_sources.md에 Seedance 2.0 프롬프트만 먼저 작성** — 생성 X
2. 사용자에게 프롬프트 + 예상 클립 수 + 예상 크레딧 **명시적으로 보고**
3. **사용자 승인 후에만** `higgsfield-generate` 스킬 호출
4. 승인 없이는 절대 자동 생성 금지 — 크레딧 소모 비용 부담 큼

### 스킬 호출 예시
```
사용자 승인 받은 후 Skill 도구로 호출:
- 스킬명: higgsfield-generate
- 입력: Seedance 2.0 프롬프트 + References 슬롯 이미지 + UI 설정 (9:16 / 720x1280 / 5초)
```

> ⚠️ 영상 생성은 **명시적 사용자 지시("생성해줘", "Higgsfield로 만들어줘") 또는 승인 체크 후에만** 진행한다.
> 04_sources.md에 프롬프트를 작성하는 것은 사전 준비 단계 → 사용자가 보고 OK해야 실제 호출.

---

## ⭐ Seedance 2.0 프롬프트 작성 가이드 (크레딧 절약 핵심)

> AI 영상 생성은 크레딧이 많이 소모되므로 **첫 시도에서 제대로 나오게** 프롬프트를 정교하게 작성한다.
> 각 클립당 비용 약 $0.30 → 잘못 생성되면 재생성 필요 → 비용 누적

### 🚨 절대 빠뜨리지 말 것 (5대 필수 요소)

매 프롬프트에 **반드시 5가지를 모두 명시**:

1. **@태그 정의 (첫 줄)**: 제품 색·디자인 명확히 묘사
2. **인물 정보**: 국적·나이대·옷차림·자세
3. **공간적 관계**: 두 물체 위치 (예: "right hand: high near face / left hand: low at waist")
4. **동작·표정**: 무엇을 하는지 + 어떤 표정
5. **카메라·비율**: "9:16 vertical portrait orientation" + 광원

### ❌ 흔한 실수 → 해결법

| 실수 | 결과 | 해결법 |
|------|------|--------|
| "holding @product" 만 | 제품을 입 앞·휴대폰 앞 등 엉뚱한 위치 | **"raised UP NEXT TO HER FACE near her right cheek"** 처럼 부위 명시 |
| 휴대폰 + 제품 같은 라인 | 두 물체 겹침 | **"fan high near face / phone low at waist"** 식 위치 분리 |
| 9:16 프롬프트만 명시 | 가로 16:9로 출력 | **UI에서 Aspect Ratio = 9:16 직접 선택** (프롬프트만으로 안 됨) |
| Reference 1장만 | 제품 OK, 자세 어색 | **References 슬롯에 제품 + 자세 reference 2장 동시 업로드** |
| Reference 이미지 더러움 | 제품에 배경 halo·노이즈 따라옴 | **깨끗한 정지 프레임 사용** (단순 배경 권장) |
| "@product is fan" 모호 | 잘못된 디자인 생성 | **"@product is the white handheld mini fan with mint green accent"** 디테일 |
| 첫 시도 즉시 재생성 | 크레딧 낭비 | **시도 전 5대 요소 체크리스트 검증 후 1번에 통과** |

### 📋 Seedance 2.0 프롬프트 템플릿 (복붙용)

```
@product is the [제품 색·디자인 디테일] (예: white handheld mini fan with mint green accent visible in the rotating fan area).
@pose shows correct posture: [자세 명시] (예: fan held next to her face cheek, blowing air toward her face from the side).

[인물 묘사] (예: A young Korean woman in her late 20s sitting on Seoul subway during summer commute).
She holds @product in her [어느 손] hand, [정확한 위치] (예: RAISED UP NEXT TO HER FACE near her right cheek, exactly like @pose).
[다른 손/물체 처리] (예: Her left hand rests on her lap / holds a smartphone DOWN AT WAIST LEVEL).
The [@product] [동작·방향] (예: blows cool air toward her face from the side).
[표정] (예: She has a refreshed slightly smiling expression).
[조명·환경] (예: Natural subway lighting through windows).
[카메라] (예: slight handheld camera movement, photorealistic vlog style, candid shot).
9:16 vertical portrait orientation, 5 seconds.
```

### 🎬 References 슬롯 활용 룰

Seedance는 최대 **9 이미지 + 3 비디오 + 3 오디오** 동시 입력 가능. 영상 1개당 권장:

| 슬롯 | 용도 | 추출 방법 |
|------|------|----------|
| Slot 1 | **@product** (제품 디테일) | 원본 영상에서 제품 정면 클로즈업 정지 프레임 |
| Slot 2 | **@pose** (자세 참조) | 원본 영상에서 의도한 자세 정지 프레임 |
| Slot 3 (선택) | 환경 참조 | 의도한 배경의 분위기 이미지 |

ffmpeg로 정지 프레임 추출 (1080x1440 업스케일):
```bash
ffmpeg -ss [초] -i input.mp4 -frames:v 1 -vf "scale=1080:1440:flags=lanczos" -q:v 1 output.png
```

### ⚙️ UI 설정 체크리스트 (UI에서 직접 선택)

프롬프트만으로 안 되고 **UI에서 직접 선택**해야 하는 항목:

- [ ] **Aspect Ratio** = `9:16` 또는 `Portrait` ⭐ 필수
- [ ] **Resolution** = 720x1280 또는 그 이상
- [ ] **Duration** = 5초 (Seedance 기본)
- [ ] **References 슬롯**에 이미지 업로드 (Slot 1 + Slot 2)

### 💰 크레딧 절약 5계명

1. **첫 시도 전 프롬프트 자가 검토** — 5대 필수 요소 누락 없는지 확인
2. **References 정성 들이기** — 깨끗한 정지 프레임 + 의도한 자세
3. **UI 설정 미리 점검** — 비율·해상도·시간 모두 맞는지
4. **시도 전 다른 사람에게 프롬프트 보여주기** — 제3자가 의도 파악 가능한지
5. **첫 결과 부족하면 프롬프트 수정 후 재시도** — 같은 프롬프트로 재시도 X

### 🎯 적합한 컷 vs 부적합한 컷

✅ **AI에 적합한 컷**:
- 일상 사용 시나리오 (지하철·사무실·카페)
- 인물의 자연스러운 동작 (잡기·보기·웃기)
- 환경 분위기 (더위·시원함)
- 빠른 컷 전환 (2~3초)

❌ **AI에 부적합한 컷** (실패율 높음):
- 제품 정면 클로즈업 (디테일 깨짐) → **원본 영상 정지 프레임 사용**
- 한국어 자막·로고가 화면에 보이는 컷 → **AI는 한글 그리기 못함**
- 빠르고 정확한 손동작 (예: 버튼 누르기) → 손가락 어색
- 5초 이상의 길고 복잡한 동작 → 누적 변형

---

## 🚨 AI 영상 톤 가이드 — UGC 리뷰 영상 느낌 (필수 준수)

> 모든 AI 영상 프롬프트(Higgsfield/Seedance/Gemini Omni Flash/Veo 공통)는 **"진짜 사람이 폰으로 찍은 숏핑 리뷰 영상"** 톤이어야 한다.
> **"Cinematic" 같은 영화적 톤은 절대 금지.** 숏핑 채널 시청자는 광고 같은 느낌에 즉시 이탈한다.

### ❌ 절대 사용 금지 키워드

| 금지 | 이유 |
|------|------|
| `cinematic`, `cinema`, `film-like` | 영화 톤 → 광고 같음 |
| `ultra-realistic cinematic portrait` | 인물 컷이 화보처럼 보임 |
| `product cinematography`, `product photography style` | 광고 컷 같음 |
| `dramatic rim light`, `dramatic side light` | 스튜디오 조명 티 |
| `golden hour`, `golden-hour backlight` | 의도된 시간대 → 광고 느낌 |
| `studio lighting`, `softbox` | 스튜디오 광고 |
| `shallow depth of field f/1.8` | 영화 카메라 스펙 |
| `color grading`, `color graded` | 후보정 티 |
| `4K cinematic look` | 영화 룩 |

### ✅ 권장 키워드 (UGC 리뷰 톤)

| 카테고리 | 권장 표현 |
|---------|-----------|
| 카메라 | `handheld iPhone-style vertical clip`, `selfie-style handheld phone shot`, `phone-shot vlog clip`, `slight phone camera shake`, `autofocus subtly adjusting` |
| 환경 | `ordinary home desk`, `ordinary bedroom or living room`, `everyday outdoor setting (street, bus stop, park)`, `casual home environment` |
| 조명 | `natural window daylight`, `natural everyday summer daylight`, `regular ceiling lamp`, `normal warm room lighting`, `NO studio lighting` |
| 스타일 | `casual Korean YouTube Shorts haul-review feel`, `Instagram Reels-style`, `authentic UGC review style`, `casual home vlog look`, `like a real Korean reviewer demonstrating ...` |
| 색감 | `raw unfiltered colors`, `no color grading`, `natural skin tones`, `realistic phone camera quality`, `raw realistic phone footage` |
| 인물 | `honest small smile`, `looks like an authentic reaction, not acted`, `slightly tired and flushed from heat` (자연스러운 표정 변화) |

### 🔄 톤 변환 예시 (Before → After)

**Before (cinematic):**
```
Cinematic close-up profile shot of a young Korean woman in her late 20s, holding a small handheld fan up to her face.
Bright sunny outdoor summer atmosphere with soft warm golden-hour backlight, shallow depth of field.
Ultra-realistic cinematic portrait, natural skin tones, gentle handheld camera feel.
```

**After (UGC 리뷰 톤):**
```
Selfie-style handheld phone clip of a young Korean woman in her late 20s, filmed by herself in an everyday outdoor summer setting (street, bus stop, or park).
She holds a small handheld fan up next to her cheek — looks like an authentic reaction, not acted.
Natural everyday summer daylight, NOT golden hour, NOT studio light.
Slight phone camera shake, casual Korean YouTube Shorts vlog look like a real summer haul review.
Realistic natural skin tones, no color grading, raw unfiltered phone footage feel.
```

### 📋 프롬프트 작성 체크리스트 (5요소 + 톤)

작성한 모든 AI 영상 프롬프트는 다음을 모두 만족해야 함:

- [ ] **카메라**: `handheld phone` 또는 `selfie-style` 명시
- [ ] **환경**: 일상 공간 (집 책상/방/거리/카페) — 스튜디오 X
- [ ] **조명**: 자연광 또는 일반 실내등 — 스튜디오 조명 X
- [ ] **스타일**: `casual Korean YouTube Shorts haul-review` 또는 동등 표현 포함
- [ ] **색감**: `raw`, `unfiltered`, `no color grading` 중 하나 이상 포함
- [ ] **금지어 0개**: 위 ❌ 표의 단어 사용 안 함

---

## 🆕 Gemini Omni Flash 활용 가이드

> Google이 출시한 신규 영상 모델. Seedance/Veo 대비 강점:
> - **최대 10초 클립** (Seedance 5초 / Veo 8초 대비 길이 우위)
> - **Multi-modal References**: 이미지 + 캐릭터 + 음성을 동시에 블렌딩
> - **Video-to-Video 편집**: 1차 생성 결과를 텍스트 명령으로 재가공 (재생성 비용 절감)
> - **Recurring Cast**: 영상 전반에 같은 인물·보컬 유지

### 🎯 우리 워크플로우 적합 컷

✅ **Gemini Omni Flash가 특히 강한 컷**:
- 인물 등장 컷 (사용 시연·외출·실내 진입) — Cast로 동일 인물 유지
- 환경 전환이 있는 컷 (야외 → 실내, 비 오는 길 → 카페) — 10초 길이로 자연스러운 전환
- 1차 결과를 부분 수정하고 싶은 컷 — V2V 편집으로 색온도/모션블러/조명만 조정

⚠️ **Seedance/Higgsfield가 더 나은 컷**:
- 제품 디테일이 핵심인 컷 (자수·로고·버튼) — Higgsfield Reference 시스템이 더 정밀
- 5초 이내 짧고 단순한 컷 — 굳이 10초 모델 쓸 필요 없음

### 📋 Gemini Omni Flash 프롬프트 작성 룰

매 프롬프트에 다음 5요소 명시:

1. **장면 도입**: 카메라 앵글 + 주체 (예: "Cinematic close-up tracking shot following a hand…")
2. **인물 정보**: 국적·성별·나이대·자세 (Recurring Cast 쓰면 `@cast_name` 호출)
3. **공간 전환**: 시작 환경 → 끝 환경 (10초 길이의 강점)
4. **조명 전환**: 시작 색온도 → 끝 색온도 (예: "cool overcast → warm golden indoor")
5. **카메라·비율**: "vertical 9:16 portrait orientation, X seconds, ultra-realistic 4K"

### 🎬 References 슬롯 활용

| 슬롯 | 용도 | 추천 소스 |
|------|------|----------|
| Ref 1 | 제품 메인 컷 | `product_images/` 폴더 또는 쿠팡 정면 캡처 |
| Ref 2 | 디테일 (자수·버튼·로고) | 쿠팡 상세 페이지 캡처 |
| Ref 3 (선택) | 환경 분위기 | Pinterest 검색 (예: "modern cafe entrance interior") |
| Cast | 인물 일관성 (영상 간 동일 캐릭터) | Cast 생성 후 `@cast_name`으로 호출 |

### 🔄 Video-to-Video 편집 활용 패턴

1차 생성 결과가 80% 만족인 경우 **재생성 대신** 텍스트 명령으로 가공:

| 의도 | 텍스트 명령 예시 |
|------|----------------|
| 색온도 조정 | "warm up the interior color temperature by 200K" |
| 부분 모션 추가 | "add subtle motion blur on the hand only" |
| 바닥/배경 보정 | "make the floor reflect more warmly" |
| 톤 리스타일 | "restyle in a cozy K-drama cinematography look" |
| 디테일 강조 | "sharpen focus on the umbrella case embroidery" |

### ⚙️ UI 설정 체크리스트

- [ ] Aspect Ratio: `9:16` (Vertical/Portrait)
- [ ] Duration: 우리 컷에 맞춰 3~5초 (또는 10초 생성 후 CapCut에서 트림)
- [ ] References 슬롯에 제품 이미지 + 환경 참조 업로드
- [ ] 인물 일관성 필요 시 Recurring Cast 사전 등록 + `@cast_name` 호출

### 💡 비용·접근

- Google AI Studio 플랜에서 사용 (Higgsfield 크레딧과 별개)
- 1회 생성으로 10초 확보 → V2V 편집 활용 시 추가 생성 비용 절감
- 웹 전용 (Agent 기능, Tools 라이브러리 모두 웹에서만)

---

## 실행 단계

### Step 1: 컷별 소스 유형 결정

03_script.md의 각 컷을 분석하여 소스 유형 매핑:
- 첫 1~3컷 (후킹): AI 영상 권장 (임팩트 필요)
- 제품 소개 컷: 쿠팡 제품 이미지 또는 직접 촬영
- 기능 시연 컷: 직접 촬영 권장 (실제감)
- 마지막 CTA 컷: 제품 메인 이미지

### Step 2: AI 이미지 프롬프트 작성 (Google Whisk)

Whisk는 텍스트가 아닌 **이미지 3장**을 슬롯에 넣는 방식이다.

| 슬롯 | 역할 | 이미지 소스 |
|------|------|------------|
| Subject | 주인공 (제품/인물) | 쿠팡 제품 이미지 캡처 |
| Scene | 배경/장면 | Google/Pinterest에서 참고 이미지 검색 |
| Style | 사진 스타일/톤 | Google에서 참고 스타일 이미지 검색 |

각 컷별로 3개 슬롯에 넣을 이미지와 검색 키워드를 구체적으로 안내한다.

### Step 2-1: AI 영상 프롬프트 작성

AI 이미지를 실사 영상 클립으로 변환한다.

**도구 선택 기준:**
- **Veo 3.1**: 사람 동작이 있는 장면 (시연, 사용, 건네기 등)
- **CapCut 내장 AI**: 제품/정물 단순 모션 (클로즈업, 패키지 등)

**Veo 3.1 프롬프트 형식:**
```
[동작 설명], [장소/배경], [조명], [카메라 앵글], [분위기]
예: "hands gently handing over a premium gift box, warm indoor lighting, close-up, soft bokeh background"
```

**프롬프트 작성 규칙:**
- 영문으로 작성
- 동작을 구체적으로 묘사 (giving, wearing, pouring 등)
- "no text, no watermark" 포함
- 세로 영상 필요 시 "vertical 9:16" 명시

### Step 3: 수집 체크리스트 작성

각 컷에 번호 매기고 수집 방법 명시.

---

## 출력 파일 형식

`workspace/{폴더}/04_sources.md`

```markdown
# 영상 소스 수집 가이드
> 제품: {제품명} | 총 컷: {N}개

---

## 컷별 소스 목록

| 컷# | 자막 | 소스 유형 | 수집 방법 |
|-----|------|-----------|-----------|
| 1 | {자막} | AI영상 | Runway 프롬프트 참고 |
| 2 | {자막} | AI이미지 | Whisk 프롬프트 참고 |
| 3 | {자막} | 제품이미지 | 쿠팡 캡처 |
| 4 | {자막} | 직접촬영 | 촬영 가이드 참고 |

---

## AI 이미지 생성 (Google Whisk)
> 접속: https://labs.google/fx/tools/whisk

### 컷 {N}: {장면 설명}
| 슬롯 | 넣을 이미지 | 설명 |
|------|------------|------|
| Subject | {제품/인물 이미지 소스} | {주인공 설명} |
| Scene | "{검색 키워드}" 참고 이미지 | {장면/배경 설명} |
| Style | "{검색 키워드}" 참고 이미지 | {스타일/톤 설명} |

---

## AI 영상 생성 (이미지 → 영상 변환)

각 AI 이미지를 실사 영상 클립으로 변환한다.

**도구 선택:**
- **Veo 3.1** (https://labs.google/fx/tools/veo) — 사람 동작이 있는 장면
- **CapCut 내장 AI** — 제품/정물 단순 모션

### 컷 {N}: {장면 설명} → **{Veo 3.1 / CapCut AI}**
```
{영문 모션 프롬프트}, vertical 9:16, no text, no watermark
```

---

## 제품 이미지 수집

| 컷# | 수집처 | 검색어 | 주의사항 |
|-----|--------|--------|----------|
| {N} | 쿠팡 | {검색어} | 판매자 이미지 사용 시 출처 확인 |

---

## 직접 촬영 가이드

촬영이 필요한 컷: {컷 번호 목록}

**촬영 팁:**
- 배경: 흰 벽 또는 깔끔한 주방/생활 공간
- 조명: 자연광 또는 링라이트 (상단)
- 앵글: 제품 정면 클로즈업 / 사용 장면 45도
- 속도: 실제보다 약간 빠르게 (1.2~1.5배속)

---

## 수집 완료 체크리스트

- [ ] 컷 1: {설명}
- [ ] 컷 2: {설명}
...

---

## TTS 음성 & SRT 자막 자동 생성

`tts_generate.py` 스크립트로 TTS 음성과 SRT 자막을 한 번에 생성한다.

```bash
# 전체 생성 (MP3 + SRT)
python3 tts_generate.py workspace/{폴더}

# 보이스/속도 변경
python3 tts_generate.py workspace/{폴더} --voice 문정 --tempo 1.3

# 특정 컷만 재생성
python3 tts_generate.py workspace/{폴더} --cut 2

# 보이스 목록 확인
python3 tts_generate.py --list-voices
```

**생성 결과물:**
- `workspace/{폴더}/audio/*.mp3` — 컷별 TTS 음성 파일
- `workspace/{폴더}/subtitle.srt` — 실제 오디오 길이 기반 SRT 자막

**SRT 자막 분할 규칙 (필수):**
- tts_generate.py가 생성한 SRT는 컷 단위로 되어 있으므로, **반드시 짧은 구절 단위로 재분할**한다
- 한 자막 단위 = **4~9자** (글자 크기 15 기준 한 줄에 표시되는 분량)
- 예: "브리타 정수기 필터 바꿀 때마다 쓰레기 죄책감 드시는 분 보세요"
  → "브리타 정수기 필터" / "바꿀 때마다" / "쓰레기 죄책감" / "드시는 분" / "보세요"
- 각 구절의 시간은 원래 컷 시간을 구절 수로 균등 분배
- CapCut에서 자막 임포트 시 SRT 파일을 드래그하면 타이밍에 맞게 자동 배치
```

---

## 완료 후 액션

04_sources.md 저장 후 shorts-pd에 완료 보고.
