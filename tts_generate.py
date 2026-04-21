#!/usr/bin/env python3
"""
숏핑 TTS 자동 생성기
03_script.md에서 나레이션을 추출하고 Typecast API로 TTS를 생성합니다.

사용법:
  python3 tts_generate.py workspace/2026-04-09_직장인활력건강템
  python3 tts_generate.py workspace/2026-04-09_직장인활력건강템 --voice 문정 --tempo 1.3
  python3 tts_generate.py workspace/2026-04-09_직장인활력건강템 --list-voices

환경변수:
  TYPEAI_API_KEY: Typecast API 키 (.env 파일 또는 환경변수)
"""

import os
import re
import sys
import json
import argparse
import requests

# .env 파일 로드
def load_dotenv(path=None):
    env_path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())

load_dotenv()

# ─── Typecast 설정 ───────────────────────────────────────

API_URL = "https://api.typecast.ai/v1/text-to-speech"

VOICES = {
    "문정": "tc_68f9c6a72f0f04a417bb136f",
    "은빈": "tc_660e45ff50e0ecacaf967d22",
    "혜민": "tc_667ce80314cb3a612d6959e8",
    "지현": "tc_65f280ecf1a9fb325938fdf9",
    "진서": "tc_65bb3a1976b69213594357fc",
    "시연": "tc_6568164fe05ddffee8b0e271",
    "이나": "tc_62686be9deec4c1bb7fd077c",
}

DEFAULTS = {
    "voice": "은빈",
    "model": "ssfm-v30",
    "language": "kor",
    "format": "mp3",
    "tempo": 1.2,
    "pitch": 0,
    "emotion": "smart",
}


# ─── 대본 파싱 ───────────────────────────────────────────

def parse_script(script_path: str) -> list[dict]:
    """03_script.md에서 컷별 나레이션과 시간 정보를 추출합니다."""
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    cuts = []
    # [시간] 구간명 패턴으로 각 섹션 분리
    sections = re.split(r'\n(?=\[)', content)

    for section in sections:
        # [0-1초] 오프닝 같은 헤더 매칭
        header_match = re.match(r'\[([^\]]+)\]\s*(.+)', section.strip())
        if not header_match:
            continue

        time_range = header_match.group(1)
        label = header_match.group(2).strip()

        # 큰따옴표로 감싼 나레이션 추출
        narration_match = re.search(r'"([^"]+(?:\n[^"]*)*)"', section)
        if not narration_match:
            continue

        narration = narration_match.group(1).strip()
        # 줄바꿈을 공백으로 변환
        narration = re.sub(r'\s*\n\s*', ' ', narration)

        cuts.append({
            "time": time_range,
            "label": label,
            "narration": narration,
        })

    return cuts


# ─── TTS 생성 ────────────────────────────────────────────

def generate_tts(
    api_key: str,
    text: str,
    voice_id: str,
    tempo: float = DEFAULTS["tempo"],
    pitch: int = DEFAULTS["pitch"],
) -> bytes:
    """Typecast API를 호출하여 TTS 오디오를 생성합니다."""
    payload = {
        "voice_id": voice_id,
        "text": text,
        "model": DEFAULTS["model"],
        "language": DEFAULTS["language"],
        "output": {
            "audio_format": DEFAULTS["format"],
            "audio_tempo": tempo,
            "audio_pitch": pitch,
        },
        "prompt": {
            "emotion_type": DEFAULTS["emotion"],
        },
    }

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Typecast API 오류 ({response.status_code}): {response.text}"
        )

    return response.content


# ─── MP3 길이 측정 ───────────────────────────────────────

def get_mp3_duration(filepath: str) -> float:
    """MP3 파일의 재생 길이(초)를 반환합니다."""
    import struct

    with open(filepath, "rb") as f:
        data = f.read()

    # MP3 프레임 헤더 파싱으로 길이 계산
    bitrate_table = {
        1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
    }
    samplerate_table = {0: 44100, 1: 48000, 2: 32000}

    total_frames = 0
    total_samples = 0
    sample_rate = 44100
    i = 0

    while i < len(data) - 4:
        # 프레임 싱크 찾기
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            header = struct.unpack(">I", data[i:i + 4])[0]
            version = (header >> 19) & 3
            layer = (header >> 17) & 3
            bitrate_idx = (header >> 12) & 0xF
            sr_idx = (header >> 10) & 3
            padding = (header >> 9) & 1

            if version == 3 and layer == 1 and bitrate_idx > 0 and bitrate_idx < 15 and sr_idx < 3:
                bitrate = bitrate_table[1][bitrate_idx] * 1000
                sample_rate = samplerate_table[sr_idx]
                frame_size = (144 * bitrate // sample_rate) + padding
                if frame_size > 0:
                    total_frames += 1
                    total_samples += 1152
                    i += frame_size
                    continue
            elif version == 2 and layer == 1 and bitrate_idx > 0 and bitrate_idx < 15 and sr_idx < 3:
                bitrate = bitrate_table[2][bitrate_idx] * 1000
                sample_rate = samplerate_table[sr_idx]
                frame_size = (144 * bitrate // sample_rate) + padding
                if frame_size > 0:
                    total_frames += 1
                    total_samples += 1152
                    i += frame_size
                    continue
        i += 1

    if total_frames == 0 or sample_rate == 0:
        # 폴백: 파일 크기 기반 추정 (128kbps 가정)
        return len(data) / (128 * 1000 / 8)

    return total_samples / sample_rate


# ─── 무음 제거 ─────────────────────────────────────────────

def trim_silence(filepath: str) -> None:
    """ffmpeg로 MP3 파일의 앞뒤 무음 구간을 제거합니다."""
    import subprocess
    import tempfile

    trimmed = filepath + ".trimmed.mp3"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", filepath,
                "-af", "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-40dB,"
                       "areverse,silenceremove=start_periods=1:start_silence=0.05:start_threshold=-40dB,areverse",
                "-q:a", "2", trimmed,
            ],
            capture_output=True,
            check=True,
        )
        os.replace(trimmed, filepath)
    except Exception:
        # ffmpeg 실패 시 원본 유지
        if os.path.exists(trimmed):
            os.remove(trimmed)


# ─── SRT 생성 ────────────────────────────────────────────

def format_srt_time(seconds: float) -> str:
    """초를 SRT 타임코드 형식(HH:MM:SS,mmm)으로 변환합니다."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = round((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(cuts: list[dict], durations: list[float]) -> str:
    """컷 목록과 각 컷의 실제 오디오 길이로 SRT 파일을 생성합니다."""
    srt = ""
    current_time = 0.0

    for i, (cut, duration) in enumerate(zip(cuts, durations), 1):
        start = format_srt_time(current_time)
        current_time += duration
        end = format_srt_time(current_time)

        # 나레이션을 자막 줄로 분리 (긴 문장은 2줄로)
        text = cut["narration"]
        if len(text) > 30:
            # 중간 지점의 공백에서 줄바꿈
            mid = len(text) // 2
            space_idx = text.find(" ", mid)
            if space_idx != -1 and space_idx < len(text) - 5:
                text = text[:space_idx] + "\n" + text[space_idx + 1:]

        srt += f"{i}\n{start} --> {end}\n{text}\n\n"

    return srt.strip()


# ─── 메인 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="숏핑 TTS 자동 생성기 — 03_script.md → MP3",
    )
    parser.add_argument(
        "workspace",
        nargs="?",
        help="작업 폴더 경로 (예: workspace/2026-04-09_직장인활력건강템)",
    )
    parser.add_argument(
        "--voice", "-v",
        default=DEFAULTS["voice"],
        help=f"보이스 이름 (기본: {DEFAULTS['voice']})",
    )
    parser.add_argument(
        "--tempo", "-t",
        type=float,
        default=DEFAULTS["tempo"],
        help=f"속도 0.5~2.0 (기본: {DEFAULTS['tempo']})",
    )
    parser.add_argument(
        "--pitch", "-p",
        type=int,
        default=DEFAULTS["pitch"],
        help=f"피치 -12~+12 (기본: {DEFAULTS['pitch']})",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="사용 가능한 보이스 목록 출력",
    )
    parser.add_argument(
        "--cut",
        type=int,
        help="특정 컷만 생성 (1부터 시작)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API 호출 없이 추출된 나레이션만 확인",
    )

    args = parser.parse_args()

    # 보이스 목록 출력
    if args.list_voices:
        print("\n🎙  사용 가능한 보이스:")
        print("-" * 30)
        for name, vid in VOICES.items():
            default = " (기본)" if name == DEFAULTS["voice"] else ""
            print(f"  {name}{default}  →  {vid}")
        print()
        return

    if not args.workspace:
        parser.print_help()
        return

    # 경로 확인
    script_path = os.path.join(args.workspace, "03_script.md")
    if not os.path.exists(script_path):
        print(f"❌ 대본 파일을 찾을 수 없습니다: {script_path}")
        sys.exit(1)

    # 보이스 확인
    if args.voice not in VOICES:
        print(f"❌ 알 수 없는 보이스: {args.voice}")
        print(f"   사용 가능: {', '.join(VOICES.keys())}")
        sys.exit(1)

    voice_id = VOICES[args.voice]

    # 대본 파싱
    cuts = parse_script(script_path)
    if not cuts:
        print("❌ 대본에서 나레이션을 추출할 수 없습니다.")
        sys.exit(1)

    print(f"\n📝 대본에서 {len(cuts)}개 컷 추출 완료")
    print(f"🎙  보이스: {args.voice} | 속도: {args.tempo}x | 피치: {args.pitch}")
    print("-" * 50)

    for i, cut in enumerate(cuts, 1):
        print(f"  [{i}] {cut['time']} {cut['label']}")
        print(f"      \"{cut['narration'][:50]}{'...' if len(cut['narration']) > 50 else ''}\"")
    print()

    if args.dry_run:
        print("✅ dry-run 완료 (API 호출 없음)")
        return

    # API 키 확인
    api_key = os.environ.get("TYPEAI_API_KEY")
    if not api_key:
        print("❌ TYPEAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 TYPEAI_API_KEY=your-api-key 추가")
        sys.exit(1)

    # 출력 폴더 생성
    audio_dir = os.path.join(args.workspace, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    # 생성할 컷 결정
    if args.cut:
        if args.cut < 1 or args.cut > len(cuts):
            print(f"❌ 컷 번호 범위 초과: {args.cut} (1~{len(cuts)})")
            sys.exit(1)
        target_cuts = [(args.cut - 1, cuts[args.cut - 1])]
    else:
        target_cuts = list(enumerate(cuts))

    # TTS 생성
    success = 0
    for idx, cut in target_cuts:
        cut_num = idx + 1
        filename = f"{cut_num:02d}_{cut['label'].replace(' ', '_').replace('—', '-')}.mp3"
        filepath = os.path.join(audio_dir, filename)

        print(f"🔊 [{cut_num}/{len(cuts)}] {cut['label']} 생성 중...")

        try:
            audio_data = generate_tts(
                api_key=api_key,
                text=cut['narration'],
                voice_id=voice_id,
                tempo=args.tempo,
                pitch=args.pitch,
            )

            with open(filepath, "wb") as f:
                f.write(audio_data)

            # 앞뒤 무음 제거
            trim_silence(filepath)

            size_kb = os.path.getsize(filepath) / 1024
            print(f"   ✅ 저장: {filepath} ({size_kb:.1f}KB)")
            success += 1

        except Exception as e:
            print(f"   ❌ 실패: {e}")

    # SRT 자막 생성 (전체 컷 생성 시에만)
    if not args.cut and success == len(cuts):
        print("📝 SRT 자막 파일 생성 중...")
        durations = []
        for idx, cut in enumerate(cuts):
            cut_num = idx + 1
            filename = f"{cut_num:02d}_{cut['label'].replace(' ', '_').replace('—', '-')}.mp3"
            filepath = os.path.join(audio_dir, filename)
            duration = get_mp3_duration(filepath)
            durations.append(duration)
            print(f"   컷 {cut_num}: {duration:.1f}초")

        srt_content = generate_srt(cuts, durations)
        srt_path = os.path.join(args.workspace, "subtitle.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        print(f"   ✅ 저장: {srt_path}")

        total_duration = sum(durations)
        print(f"   총 나레이션 길이: {total_duration:.1f}초")

    print()
    print(f"{'=' * 50}")
    print(f"🎉 TTS 생성 완료: {success}/{len(target_cuts)}개 성공")
    print(f"📁 저장 위치: {audio_dir}/")
    if not args.cut and success == len(cuts):
        print(f"📝 자막 파일: {os.path.join(args.workspace, 'subtitle.srt')}")
    print()


if __name__ == "__main__":
    main()
