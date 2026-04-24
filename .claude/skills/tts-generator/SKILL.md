---
name: tts-generator
description: >
  03_script.md 대본을 Typecast API로 TTS 음성(mp3)과 SRT 자막 파일로 자동 변환하는 에이전트.
  script-writer 완료 후 자동 호출되어 `tts_generate.py` + `split_srt.py`를 실행한다.
  사용자가 대본 수정을 확정한 직후에 실행하며, 수동 Typecast 작업을 완전히 대체한다.
---

# TTS & 자막 자동 생성기

## 역할

`03_script.md` 대본을 입력받아 다음 두 가지 산출물을 자동 생성한다:

1. **컷별 음성 파일 (mp3)** — `audio/` 폴더에 컷별 저장
2. **SRT 자막 파일** — `subtitle.srt` (4~9자 짧은 구절로 분할된 상태)

ffmpeg 후처리로 앞뒤 무음을 자동 제거하고, 실제 오디오 길이 기반으로 SRT 타이밍을 정확히 맞춘다.

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

> ⚠️ **테이블 형식(`| 1 | 나레이션 | ... |`)은 파싱 실패한다.**
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
3. `.env` 파일에 `TYPEAI_API_KEY`가 설정되어 있는지 확인

```bash
# API 키 확인
grep TYPEAI_API_KEY /path/to/.env
```

### Step 2: TTS + SRT 자동 생성

```bash
cd /Users/trinity/Documents/LLM\ Vault/Projects/ShortFlow/shortping-gen
python3 tts_generate.py "workspace/{폴더명}"
```

- 컷 수만큼 Typecast API 호출 (컷당 약 2~3초 소요)
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

사용자에게 결과 요약:

```
🎙 TTS 생성 완료
- 음성 파일: N개 (audio/)
- 자막 파일: subtitle.srt (M개 구절)
- 총 나레이션 길이: X.X초
- 보이스: 은빈 | 속도: 1.2x
```

---

## 옵션 (tts_generate.py 인자)

```bash
# 보이스 변경 (기본: 은빈)
python3 tts_generate.py workspace/{폴더} --voice 문정

# 속도 변경 (기본: 1.2)
python3 tts_generate.py workspace/{폴더} --tempo 1.3

# 피치 변경 (기본: 0, 범위: -12 ~ +12)
python3 tts_generate.py workspace/{폴더} --pitch 2

# 사용 가능한 보이스 목록
python3 tts_generate.py --list-voices
```

### 사용 가능한 보이스

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

## split_srt.py 옵션

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
[Step 3] tts-generator (본 스킬)   → audio/ + subtitle.srt
    ↓
[Step 4] source-collector    → 04_sources.md
```

---

## 비용

- **Typecast API 비용만 발생** (영상당 약 ₩500~1,000)
- Claude 호출 비용 없음 (Max 플랜)

---

## 에러 처리

### "TYPEAI_API_KEY 환경변수가 설정되지 않았습니다"
→ `.env` 파일에 API 키 추가:
```
TYPEAI_API_KEY=sk-xxxxxxxxxxxx
```

### "대본에서 컷을 추출하지 못했습니다"
→ 대본이 `[시간] 구간` + `"나레이션"` 형식인지 확인.
테이블 형식이면 script-writer에게 재작성 요청.

### "Typecast API 오류"
→ API 키 유효성, 계정 크레딧 잔액 확인.

### "ffmpeg 명령을 찾을 수 없습니다"
→ `brew install ffmpeg` 실행 후 재시도.

---

## 완료 후 액션

audio/ 폴더와 subtitle.srt 생성 완료 후:
- 결과를 사용자에게 요약 보고
- 자동으로 다음 단계(source-collector)로 진행
