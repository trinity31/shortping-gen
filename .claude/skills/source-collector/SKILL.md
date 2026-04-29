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

---

## 입력

- `workspace/{폴더}/03_script.md` — 최종 대본 (컷 설명 포함)

---

## 소스 유형 분류

| 유형 | 도구 | 비용 | 용도 |
|------|------|------|------|
| AI 이미지 | Google Whisk AI | 무료 | 정지 이미지 생성 (영상 변환 전 단계) |
| AI 영상 (실사·제품 일관) | **Seedance 2.0 (ByteDance)** | $0.30/클립 | 제품 + 인물 + 환경 일관, References 시스템 ⭐ |
| AI 영상 (실사) | Google Veo 3.1 | 무료 | 사람 동작이 있는 시연/사용 장면 |
| AI 영상 (모션) | CapCut 내장 AI | 무료 | 제품/정물 단순 모션 |
| 제품 이미지 | 쿠팡/네이버 스토어 캡처 | 무료 (저작권 확인) | 제품 패키지, 리뷰 캡처 |
| 직접 촬영 | 스마트폰 | 무료 | 실제 사용 시연, 표정 |

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
