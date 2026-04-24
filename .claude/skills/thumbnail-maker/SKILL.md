---
name: thumbnail-maker
description: >
  숏핑 쇼츠 썸네일 이미지를 자동 생성하는 에이전트.
  업로드_정보.md 생성 직후 자동 호출되어 `thumbnail_generate.py`를 실행한다.
  제품 이미지와 텍스트를 합성하여 1080x1920 썸네일을 만든다. 수동 디자인 불필요.
---

# 썸네일 자동 생성기

## 역할

업로드_정보.md의 썸네일 문구와 `product_images/` 폴더의 제품 이미지를 합성하여
YouTube Shorts 썸네일 이미지(1080x1920)를 자동 생성한다.

**upload-manager 완료 직후 자동 호출되며, 사용자 확인 없이 실행된다.**

---

## 입력

- `workspace/{폴더}/업로드_정보.md` — 썸네일 문구
- `workspace/{폴더}/product_images/` — 제품 이미지 (번호순 정렬, 최대 3개)
  - 예: `1_멀티비타민.jpg`, `2_아이마스크.jpg`, `3_마사지기.jpg`
  - 폴더 없으면 자동 생성됨

---

## 사용법

```bash
# 기본 생성 (업로드_정보.md에서 추천 문구 사용)
python3 thumbnail_generate.py workspace/{폴더}

# 문구 직접 지정
python3 thumbnail_generate.py workspace/{폴더} --line1 "직장인 건강 꿀템" --line2 "이 3개면 달라짐"

# 색상 변경
python3 thumbnail_generate.py workspace/{폴더} --accent "#FF4444" --border "#FF4444"

# 제품 이미지 없이 텍스트만 (배경 그라데이션)
python3 thumbnail_generate.py workspace/{폴더} --no-images
```

---

## 디자인 규칙

### 레이아웃 (ShortFlow 앱과 동일)
- 캔버스: 1080x1920 (9:16)
- 제품 이미지를 1~3개 섹션으로 균등 분할
- 각 섹션에 제품 이미지를 cover 모드로 배치
- 이미지 위에 어두운 그라데이션 오버레이
- 텍스트는 화면 중앙에 -2도 회전

### 텍스트 스타일
- 폰트: 굵은 고딕 (Apple SD Gothic Neo 또는 시스템 폰트)
- 크기: 캔버스 너비의 11%
- 색상: 흰색 (첫/마지막 줄), 강조색 (중간 줄)
- 테두리: 흰색 외곽 + 검정 내곽 (3패스 스트로크)

### 색상 프리셋
| 이름 | 코드 | 용도 |
|------|------|------|
| 노란색 | #FFD600 | 기본 강조색 |
| 빨간색 | #FF4444 | 긴급/할인 느낌 |
| 민트 | #00BFA5 | 건강/청량 |
| 보라 | #AA00FF | 프리미엄 |

---

## 출력

- `workspace/{폴더}/thumbnail.png` — 생성된 썸네일 이미지

---

## 워크플로우

1. `업로드_정보.md`에서 썸네일 문구 추출
2. `product_images/` 폴더에서 제품 이미지 로드
3. 캔버스 생성 → 이미지 배치 → 오버레이 → 텍스트 합성
4. `thumbnail.png`로 저장

---

## 호출 시점

shorts-pd 또는 `/make-video` 커맨드의 **Step 7(upload-manager) 완료 직후** 자동 호출된다.

```
[Step 7] upload-manager     → 업로드_정보.md
    ↓ 자동 호출
[Step 8] thumbnail-maker ⚙️  → thumbnail.png
```

> 사용자 확인 없이 자동 실행. `product_images/` 폴더가 비어 있으면 안내만 남기고 스킵.

---

## 사전 조건 체크

1. `workspace/{폴더}/업로드_정보.md` 존재 여부 (썸네일 문구 추출)
2. `workspace/{폴더}/product_images/` 폴더 존재 여부
   - 없으면 자동 생성하고 사용자 안내:
     > "⚠️ `product_images/` 폴더에 제품 이미지를 넣어주세요. 파일명 예: `1_제품명.jpg`, `2_제품명.jpg`"
   - 이미지 1~3개 있으면 바로 실행
