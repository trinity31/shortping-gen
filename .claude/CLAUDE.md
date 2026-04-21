# ShortFlow 하네스 — Claude Code 개발 지침

## 프로젝트 개요

- **프로젝트명**: ShortFlow
- **목적**: 숏핑(쇼핑 쇼츠) 유튜브 영상 제작 전체 워크플로우 자동화
- **핵심 원칙**: Claude Max 플랜으로 API 비용 없이 운영 (TTS 비용만 발생)

---

## 하네스 구조

```
ShortFlow/
├── CLAUDE.md                          # 이 파일
├── .claude/
│   └── skills/
│       ├── shorts-pd/SKILL.md         # 메인 오케스트레이터 (진입점)
│       ├── trend-researcher/SKILL.md  # 트렌드 제품 발굴
│       ├── reference-analyzer/SKILL.md # 레퍼런스 영상 분석
│       ├── script-writer/SKILL.md     # 대본 작성
│       ├── source-collector/SKILL.md  # 소스 수집 가이드
│       ├── edit-guide/SKILL.md        # CapCut 편집 가이드
│       └── upload-manager/SKILL.md    # 업로드 정보 생성
└── workspace/
    └── {YYYY-MM-DD}_{제품명}/         # 영상별 작업 폴더
        ├── 01_products.md
        ├── 02_reference.md
        ├── 03_script.md
        ├── 04_sources.md
        ├── 05_edit_guide.md
        ├── 업로드_정보.md
        ├── sources/                       # 영상 소스 보관
        └── final/                         # 완성 영상 보관
```

---

## 시작 방법

Claude Code에서 이 폴더를 열고:

```
영상 만들어줘
```

→ shorts-pd 스킬이 자동 실행되어 전체 워크플로우 시작.

---

## 에이전트 역할 분담

| 에이전트 | 역할 | 비용 |
|----------|------|------|
| shorts-pd | 전체 오케스트레이션 | ₩0 (Max) |
| trend-researcher | 구독 채널 트렌드 분석 | ₩0 (Max) |
| reference-analyzer | 레퍼런스 영상 분석 | ₩0 (Max) |
| script-writer | 대본 작성 | ₩0 (Max) |
| source-collector | AI 이미지 프롬프트 생성 | ₩0 (Max) |
| edit-guide | CapCut 편집 가이드 | ₩0 (Max) |
| upload-manager | 업로드 정보 생성 | ₩0 (Max) |
| **Typecast TTS** | 음성 나레이션 | **₩500~1,000/영상** |
| Google Whisk AI | 이미지 생성 | ₩0 (무료) |

**영상 1개당 총 비용: ₩500~1,500** (기존 ShortFlow API 방식 대비 약 70~90% 절감)

---

## 컨텍스트 전달 방식

에이전트 간 컨텍스트는 **MD 파일**로 전달한다.
각 에이전트는 이전 단계 MD 파일을 읽고 작업 후 다음 MD 파일을 생성.
Context Rot 방지를 위해 각 에이전트는 필요한 파일만 읽는다.

---

## 사용자 개입 시점

자율 진행하되 3번만 확인:
1. **제품 선택**: trend-researcher 완료 후 (어떤 제품 제작할지)
2. **대본 검토**: script-writer 완료 후 (수정 사항 반영)
3. **최종 확인**: upload-manager 완료 후 (전체 패키지 확인)

---

## 외부 도구 연동

| 도구 | 용도 | 접속 |
|------|------|------|
| Typecast | TTS 음성 생성 | https://typecast.ai |
| Google Whisk | AI 이미지 생성 | https://labs.google/fx/tools/whisk |
| CapCut | 영상 편집 | 데스크톱 앱 |
| 쿠팡 파트너스 | 수익화 링크 | https://partners.coupang.com |

---

## 숏핑 채널 컨텍스트

- **채널 스타일**: 생활/주방/뷰티 꿀템 쇼핑 쇼츠
- **수익 모델**: 쿠팡 파트너스 링크 커미션
- **영상 길이**: 22~60초
- **클로징 CTA**: "제품정보는 프로필 링크에!"
- **오프닝 포맷**: "삶의 질 확 올라가는 {카테고리} 꿀템 {N}가지"
