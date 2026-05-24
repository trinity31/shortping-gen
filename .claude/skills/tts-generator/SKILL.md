---
name: tts-generator
description: >
  03_script.md 대본을 TTS API로 음성(mp3)과 SRT 자막 파일로 자동 변환하는 에이전트.
  script-writer 완료 후 자동 호출되어 `tts_generate.py`(~2026-06-20) 또는 `supertonic_generate.py`(2026-06-21~)를 실행한다.
  사용자가 대본 수정을 확정한 직후에 실행하며, 수동 TTS 작업을 완전히 대체한다.
---

# TTS & 자막 자동 생성기

## 역할

`03_script.md` 대본을 입력받아 다음 두 가지 산출물을 자동 생성한다:

1. **컷별 음성 파일 (mp3)** — `audio/` 폴더에 컷별 저장
2. **SRT 자막 파일** — `subtitle.srt` (4~9자 짧은 구절로 분할된 상태)

ffmpeg 후처리로 앞뒤 무음을 자동 제거하고, 실제 오디오 길이 기반으로 SRT 타이밍을 정확히 맞춘다.

---

## 🗓 엔진 선택 룰 (오늘 날짜 기준)

| 기간 | 메인 엔진 | 스크립트 | 환경변수 | 보이스 | 비용 |
|------|----------|---------|---------|--------|------|
| **~ 2026-06-20** ⭐ | **Typecast** | `tts_generate.py` | `TYPEAI_API_KEY` | 은빈 / ssfm-v30 / tempo 1.2 | 영상당 ₩500~1,000 |
| **2026-06-21 ~** | Supertone | `supertonic_generate.py` | `SUPERTONIC_API_KEY` | Dasom / sona_speech_2 / speed 1.2 | API 사용량 기반 |

> Typecast 플랜이 2026-06-20에 종료되므로 그 다음 날부터 Supertone으로 자동 전환.
> 본 스킬이 호출될 때 오늘 날짜를 확인해서 올바른 스크립트를 선택해 실행한다.

---

## 입력

- `workspace/{폴더}/03_script.md` — 대본 (**필수: `[시간] 구간명` + `"나레이션"` 형식**)

### 입력 대본 형식 (파서 요구사항)

```markdown
[0~3초] 컷 1 — 공감 훅
"요즘 햇빛 진짜 너무 강하죠?"
💚 화면: ...

[3~5초] 컷 2 — 문제 제기
"몸에도 선크림 발라야 한다는데"
💚 화면: ...
```

> ⚠️ **테이블 형식(`| 1 | 나레이션 | ... |`)은 두 스크립트 모두 파싱 실패한다.**
> script-writer가 생성한 대본은 반드시 위 형식이어야 한다.

---

## 출력

```
workspace/{폴더}/
├── audio/
│   ├── 01_컷_1_-_공감_훅.mp3
│   ├── 02_컷_2_-_문제_제기.mp3
│   └── ... (컷 수만큼)
└── subtitle.srt   (4~9자 짧은 구절로 분할됨)
```

---

## 실행 단계

### Step 1: 사전 검증

1. `03_script.md`가 존재하는지 확인
2. 대본이 `[시간] 구간` 형식인지 확인 (테이블 형식이면 사용자에게 경고)
3. **오늘 날짜 확인 → 엔진 결정**
4. `.env` 파일에 해당 엔진의 API 키가 설정되어 있는지 확인

```bash
# 오늘 날짜 기준 API 키 확인
grep TYPEAI_API_KEY /path/to/.env      # ~2026-06-20
grep SUPERTONIC_API_KEY /path/to/.env  # 2026-06-21~
```

### Step 2: TTS + SRT 자동 생성

**~ 2026-06-20 (현재 메인) — Typecast 은빈:**
```bash
cd /Users/trinity/Documents/LLM\ Vault/Projects/ShortFlow/shortping-gen
python3 tts_generate.py "workspace/{폴더명}"
```

**2026-06-21 ~ — Supertone Dasom (audio/ 출력으로 옵션 지정):**
```bash
cd /Users/trinity/Documents/LLM\ Vault/Projects/ShortFlow/shortping-gen
python3 supertonic_generate.py "workspace/{폴더명}" --output-dir audio --srt-name subtitle.srt
```

공통 동작:
- 컷 수만큼 API 호출 (컷당 약 2~3초 소요)
- 각 mp3의 앞뒤 무음 자동 제거(ffmpeg)
- 실제 오디오 길이 기반 `subtitle.srt` 생성

### Step 3: SRT 짧은 구절 분할

```bash
python3 split_srt.py "workspace/{폴더명}"
```

- 컷 단위 SRT → 4~9자 짧은 구절 단위로 재분할
- 살림토끼 스타일 가독성 확보
- 원래 컷 시간을 구절 수로 균등 분배

### Step 4: 결과 보고

사용자에게 결과 요약 (사용된 엔진 명시):

```
🎙 TTS 생성 완료 (엔진: Typecast 은빈 / Supertone Dasom)
- 음성 파일: N개 (audio/)
- 자막 파일: subtitle.srt (M개 구절)
- 총 나레이션 길이: X.X초
- 보이스: 은빈 (Typecast) | 속도: 1.2x
   또는
- 보이스: Dasom (Supertone) | 모델: sona_speech_2 | 속도: 1.2x
```

---

## Typecast 옵션 (tts_generate.py 인자, ~2026-06-20)

```bash
# 보이스 변경 (기본: 은빈)
python3 tts_generate.py workspace/{폴더} --voice 문정

# 속도 변경 (기본: 1.2, 범위: 0.5 ~ 2.0)
python3 tts_generate.py workspace/{폴더} --tempo 1.3

# 피치 변경 (기본: 0, 범위: -12 ~ +12)
python3 tts_generate.py workspace/{폴더} --pitch 2

# 사용 가능한 보이스 목록
python3 tts_generate.py --list-voices
```

### Typecast 사용 가능한 보이스

| 이름 | 특징 |
|------|------|
| 은빈 ⭐ | 30대 여성, 친근·밝은 톤 (기본, 살림토끼 무드) |
| 문정 | 차분·진중 |
| 혜민 | 젊고 발랄 |
| 지현 | 감성적 |
| 진서 | 또렷·신뢰감 |
| 시연 | 친근·수다스러운 |
| 이나 | 쿨·담담 |

---

## Supertone 옵션 (supertonic_generate.py 인자, 2026-06-21~)

```bash
# 메인 사용 — audio/, subtitle.srt로 표준 출력
python3 supertonic_generate.py workspace/{폴더} --output-dir audio --srt-name subtitle.srt

# 속도 변경 (기본: 1.2, 범위: 0.5 ~ 2.0)
python3 supertonic_generate.py workspace/{폴더} --speed 1.3 --output-dir audio --srt-name subtitle.srt

# 모델 변경 (기본: sona_speech_2)
python3 supertonic_generate.py workspace/{폴더} --model sona_speech_2_flash --output-dir audio --srt-name subtitle.srt

# 다른 보이스 사용 (voice_id 직접 지정)
python3 supertonic_generate.py workspace/{폴더} --voice-id <voice_id> --output-dir audio --srt-name subtitle.srt

# 스타일 변경 (기본: neutral, 옵션: happy / angry / sad)
python3 supertonic_generate.py workspace/{폴더} --style happy --output-dir audio --srt-name subtitle.srt
```

### Supertone 기본 보이스 (채널 표준, 2026-06-21~)

| 항목 | 값 |
|------|-----|
| 이름 | **[New] Dasom** |
| voice_id | `4680c81c69d8490a044413` |
| gender / age | female / young-adult |
| 모델 | `sona_speech_2` (차세대 추천) |
| 스타일 | `neutral` |
| 속도 | `1.2x` |
| 음높이 | `0` (기본) |
| 음높이 변화 | `1.0` (기본) |

### Supertone 다른 한국어 보이스 후보 (참고)

| 이름 | voice_id | 톤 |
|------|----------|-----|
| [Choice] Yejin | `c9220df3a5a70647d7b022` | happy/angry/sad 다양 |
| [Choice] Tilly | `084714312eb4ec06fbfe51` | happy/shy 친근 |
| Selena | `2d172d6efe637391880b10` | happy/kind/teasing |
| Audrey | `1f6b70f879da125bfec245` | confident/happy (단정형) |
| Lina | `bfa99ca4788be7104dd324` | happy/curious (의문형) |

> 보이스 후보 추가 탐색은 `GET https://supertoneapi.com/v1/voices` 호출 결과 참고.

---

## split_srt.py 옵션 (공통)

```bash
# 구절 길이 변경 (기본: 4~9자)
python3 split_srt.py workspace/{폴더} --min 5 --max 10

# 입력·출력 파일 지정
python3 split_srt.py workspace/{폴더} --in subtitle.srt --out subtitle.srt
```

---

## 호출 시점

shorts-pd 또는 `/make-video` 커맨드의 **Step 2(대본 작성) 완료 + 사용자 수정 확정 직후** 자동 호출된다.

```
[Step 2] script-writer       → 03_script.md
    ↓ 사용자 수정 확정
[Step 3] tts-generator (본 스킬)   → 오늘 날짜 확인 → audio/ + subtitle.srt
    ↓
[Step 4] source-collector    → 04_sources.md
```

---

## 비용

- **~ 2026-06-20**: Typecast 영상당 약 ₩500~1,000 (메인)
- **2026-06-21 ~**: Supertone API 사용량 기반 (메인 전환)
- Claude 호출 비용 없음 (Max 플랜)

---

## 에러 처리

### "TYPEAI_API_KEY 환경변수가 설정되지 않았습니다" (~2026-06-20)
→ `.env` 파일에 API 키 추가:
```
TYPEAI_API_KEY=<your-typecast-key>
```

### "SUPERTONIC_API_KEY 환경변수가 설정되지 않았습니다" (2026-06-21~)
→ `.env` 파일에 API 키 추가:
```
SUPERTONIC_API_KEY=<your-supertone-key>
```

### "대본에서 컷을 추출하지 못했습니다"
→ 대본이 `[시간] 구간` + `"나레이션"` 형식인지 확인.
테이블 형식이면 script-writer에게 재작성 요청.

### "API 오류"
→ API 키 유효성, 계정 크레딧 잔액 확인.

### "텍스트 300자 초과" (Supertone 한정)
→ Supertone은 요청당 최대 300자. 우리 컷은 평균 20~30자라 정상이면 안 걸림.
→ 한 컷에 한 문장(대본 한 줄) 원칙 위반인지 확인.

### "ffmpeg 명령을 찾을 수 없습니다"
→ `brew install ffmpeg` 실행 후 재시도.

---

## 완료 후 액션

audio/ 폴더와 subtitle.srt 생성 완료 후:
- 결과를 사용자에게 요약 보고 (사용된 엔진·보이스·속도 명시)
- 자동으로 다음 단계(source-collector)로 진행
