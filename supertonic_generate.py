#!/usr/bin/env python3
"""
숏핑 TTS 자동 생성기 (Supertone API)
03_script.md에서 나레이션을 추출하고 Supertone API로 TTS를 생성합니다.

사용법:
  python3 supertonic_generate.py workspace/2026-05-22_미니덕트_손선풍기
  python3 supertonic_generate.py workspace/... --voice-id <id> --model sona_speech_1 --style happy

환경변수:
  SUPERTONIC_API_KEY: Supertone API 키 (.env 또는 환경변수)
"""

import os
import sys
import argparse
import requests

# tts_generate.py에서 공용 유틸 재사용 (DRY)
from tts_generate import (
    load_dotenv,
    parse_script,
    get_mp3_duration,
    trim_silence,
    generate_srt,
)

load_dotenv()

# ─── Supertone 설정 ──────────────────────────────────────

API_BASE = "https://supertoneapi.com/v1/text-to-speech"

DEFAULTS = {
    "voice_id": "4680c81c69d8490a044413",   # [New] Dasom (사용자 선택)
    "model": "sona_speech_2",
    "style": "neutral",
    "language": "ko",
    "output_format": "mp3",
    "speed": 1.2,
    "pitch_shift": 0,
    "pitch_variance": 1.0,
    "output_dir": "audio_supertone",        # 기본은 분리 폴더 (Typecast audio/ 보존)
    "srt_name": "subtitle_supertone.srt",   # 2026-06-21부터 메인 전환 시 --output-dir audio --srt-name subtitle.srt 지정
}


# ─── TTS 생성 ────────────────────────────────────────────

def generate_tts(
    api_key: str,
    text: str,
    voice_id: str,
    model: str,
    style: str,
    speed: float,
    pitch_shift: int,
    pitch_variance: float,
    output_format: str,
) -> tuple[bytes, float | None]:
    """Supertone API 호출. (audio_bytes, audio_length_seconds) 반환."""
    url = f"{API_BASE}/{voice_id}"
    payload = {
        "text": text,
        "language": DEFAULTS["language"],
        "style": style,
        "model": model,
        "output_format": output_format,
        "voice_settings": {
            "pitch_shift": pitch_shift,
            "pitch_variance": pitch_variance,
            "speed": speed,
        },
    }
    headers = {
        "x-sup-api-key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Supertone API 오류 ({response.status_code}): {response.text[:300]}"
        )

    # X-Audio-Length 헤더 (초)
    raw_len = response.headers.get("X-Audio-Length")
    audio_length = float(raw_len) if raw_len else None
    return response.content, audio_length


# ─── 메인 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="숏핑 TTS 자동 생성기 (Supertone) — 03_script.md → MP3",
    )
    parser.add_argument("workspace", nargs="?", help="작업 폴더 경로")
    parser.add_argument("--voice-id", default=DEFAULTS["voice_id"])
    parser.add_argument("--model", default=DEFAULTS["model"],
                        choices=["sona_speech_1", "sona_speech_2", "sona_speech_2_flash", "supertonic_api_1"])
    parser.add_argument("--style", default=DEFAULTS["style"])
    parser.add_argument("--speed", "-t", type=float, default=DEFAULTS["speed"], help="0.5~2.0")
    parser.add_argument("--pitch-shift", type=int, default=DEFAULTS["pitch_shift"], help="-24~24 반음")
    parser.add_argument("--pitch-variance", type=float, default=DEFAULTS["pitch_variance"], help="0~2")
    parser.add_argument("--output-format", default=DEFAULTS["output_format"], choices=["mp3", "wav"])
    parser.add_argument("--output-dir", default=DEFAULTS["output_dir"], help="컷별 음성 저장 폴더명")
    parser.add_argument("--srt-name", default=DEFAULTS["srt_name"], help="SRT 파일명")
    parser.add_argument("--cut", type=int, help="특정 컷만 생성 (1부터)")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not args.workspace:
        parser.print_help()
        return

    script_path = os.path.join(args.workspace, "03_script.md")
    if not os.path.exists(script_path):
        print(f"❌ 대본 파일 없음: {script_path}")
        sys.exit(1)

    cuts = parse_script(script_path)
    if not cuts:
        print("❌ 대본에서 나레이션을 추출할 수 없습니다.")
        sys.exit(1)

    print(f"\n📝 대본에서 {len(cuts)}개 컷 추출")
    print(f"🎙  Supertone | voice_id={args.voice_id} | model={args.model}")
    print(f"   style={args.style} | speed={args.speed}x | pitch_shift={args.pitch_shift} | pitch_variance={args.pitch_variance}")
    print("-" * 50)

    for i, cut in enumerate(cuts, 1):
        print(f"  [{i}] {cut['time']} {cut['label']}")
        print(f"      \"{cut['narration'][:50]}{'...' if len(cut['narration']) > 50 else ''}\"")
    print()

    if args.dry_run:
        print("✅ dry-run 완료")
        return

    api_key = os.environ.get("SUPERTONIC_API_KEY")
    if not api_key:
        print("❌ SUPERTONIC_API_KEY가 설정되지 않았습니다 (.env 확인)")
        sys.exit(1)

    audio_dir = os.path.join(args.workspace, args.output_dir)
    os.makedirs(audio_dir, exist_ok=True)

    if args.cut:
        if args.cut < 1 or args.cut > len(cuts):
            print(f"❌ 컷 번호 범위 초과: {args.cut} (1~{len(cuts)})")
            sys.exit(1)
        target_cuts = [(args.cut - 1, cuts[args.cut - 1])]
    else:
        target_cuts = list(enumerate(cuts))

    ext = args.output_format
    success = 0
    api_lengths: dict[int, float] = {}

    for idx, cut in target_cuts:
        cut_num = idx + 1
        safe_label = cut["label"].replace(" ", "_").replace("—", "-").replace("/", "_")
        filename = f"{cut_num:02d}_{safe_label}.{ext}"
        filepath = os.path.join(audio_dir, filename)

        print(f"🔊 [{cut_num}/{len(cuts)}] {cut['label']} 생성 중...")
        try:
            audio_data, api_len = generate_tts(
                api_key=api_key,
                text=cut["narration"],
                voice_id=args.voice_id,
                model=args.model,
                style=args.style,
                speed=args.speed,
                pitch_shift=args.pitch_shift,
                pitch_variance=args.pitch_variance,
                output_format=ext,
            )
            with open(filepath, "wb") as f:
                f.write(audio_data)

            if ext == "mp3":
                trim_silence(filepath)

            if api_len is not None:
                api_lengths[idx] = api_len

            size_kb = os.path.getsize(filepath) / 1024
            len_str = f" | API: {api_len:.2f}s" if api_len else ""
            print(f"   ✅ {filepath} ({size_kb:.1f}KB){len_str}")
            success += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")

    # SRT 자막 생성 (전체 컷 + mp3만)
    if not args.cut and success == len(cuts) and ext == "mp3":
        print("📝 SRT 자막 파일 생성 중...")
        durations = []
        for idx, cut in enumerate(cuts):
            cut_num = idx + 1
            safe_label = cut["label"].replace(" ", "_").replace("—", "-").replace("/", "_")
            filename = f"{cut_num:02d}_{safe_label}.{ext}"
            filepath = os.path.join(audio_dir, filename)
            # 무음 제거 후 길이가 정확하므로 파일에서 다시 측정
            duration = get_mp3_duration(filepath)
            durations.append(duration)
            print(f"   컷 {cut_num}: {duration:.1f}초")

        srt_content = generate_srt(cuts, durations)
        srt_path = os.path.join(args.workspace, args.srt_name)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"   ✅ 저장: {srt_path}")
        print(f"   총 나레이션 길이: {sum(durations):.1f}초")

    print()
    print("=" * 50)
    print(f"🎉 Supertone TTS 생성 완료: {success}/{len(target_cuts)}개")
    print(f"📁 저장 위치: {audio_dir}/")
    if not args.cut and success == len(cuts) and ext == "mp3":
        print(f"📝 자막 파일: {os.path.join(args.workspace, args.srt_name)}")
    print()


if __name__ == "__main__":
    main()
