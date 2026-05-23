#!/usr/bin/env python3
"""
auto_edit.py — 05_edit_guide.md 기반 FFmpeg 자동 편집

CapCut 수동 편집을 대체한다. 가이드의 컷별 추출 구간 + audio/*.mp3 +
ai_clips/cut{N}_*.mp4 + subtitle.srt를 조합해 1080x1920 30fps MP4로 출력한다.

사용법:
    python3 auto_edit.py "workspace/2026-04-27_미스트선풍기"
    python3 auto_edit.py "workspace/2026-04-27_미스트선풍기" --dry-run
    python3 auto_edit.py "workspace/2026-04-27_미스트선풍기" --keep-temp
    python3 auto_edit.py "workspace/2026-04-27_미스트선풍기" --no-subtitles
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys


CANVAS_W = 1080
CANVAS_H = 1920
FPS = 30
SUBTITLE_FONT = "AppleSDGothicNeo-Bold"
SUBTITLE_FORCE_STYLE = (
    f"FontName={SUBTITLE_FONT},FontSize=18,"
    "PrimaryColour=&Hffffff&,OutlineColour=&H000000&,"
    "BorderStyle=1,Outline=3,Shadow=1,Alignment=10,MarginV=0"
)


# ─── 파싱 ─────────────────────────────────────────────────

CUT_HEADER_RE = re.compile(
    r"^###\s+컷\s+(\d+)\s+—\s+"
    r"(\d+):(\d+(?:\.\d+)?)\s*~\s*"
    r"(\d+):(\d+(?:\.\d+)?)\s*"
    r"\(([\d.]+)초\)"
)
MP3_RE = re.compile(r"\*\*mp3\*\*:\s*`([^`]+)`")
EXTRACT_RE = re.compile(r"\*\*추출 구간\*\*:\s*영상\s*\*\*([\d.]+)\s*~\s*([\d.]+)초\*\*")
AI_RE = re.compile(r"AI 실사 컷|\*\*소스\*\*:\s*\*\*AI 생성\*\*")


def timeline_to_seconds(minutes: str, seconds: str) -> float:
    return int(minutes) * 60 + float(seconds)


def parse_edit_guide(path: str) -> list[dict]:
    """05_edit_guide.md를 파싱해 컷 리스트를 반환한다.

    각 컷 dict:
      cut_no: int
      timeline_start, timeline_end, timeline_duration: float
      mp3: str (파일명, audio/ 폴더 기준)
      is_ai: bool
      source_in, source_out: float (일반 컷일 때만)
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # 컷별로 본문을 분할
    lines = content.splitlines()
    cuts: list[dict] = []
    current: dict | None = None
    body_lines: list[str] = []

    def finalize(cut: dict, body: list[str]) -> None:
        joined = "\n".join(body)
        m = MP3_RE.search(joined)
        if not m:
            raise ValueError(f"컷 {cut['cut_no']}: mp3 항목을 찾지 못했습니다")
        cut["mp3"] = m.group(1)

        cut["is_ai"] = bool(AI_RE.search(joined))

        ext = EXTRACT_RE.search(joined)
        if ext:
            cut["source_in"] = float(ext.group(1))
            cut["source_out"] = float(ext.group(2))
        else:
            # 추출 구간이 없으면 AI 컷으로 간주
            cut["is_ai"] = True

        cuts.append(cut)

    for line in lines:
        m = CUT_HEADER_RE.match(line)
        if m:
            if current is not None:
                finalize(current, body_lines)
            cut_no = int(m.group(1))
            start = timeline_to_seconds(m.group(2), m.group(3))
            end = timeline_to_seconds(m.group(4), m.group(5))
            current = {
                "cut_no": cut_no,
                "timeline_start": start,
                "timeline_end": end,
                "timeline_duration": end - start,
            }
            body_lines = []
        elif current is not None:
            # 다음 ### 섹션(컷이 아닌)에서 종료
            if line.startswith("## ") or (line.startswith("### ") and not CUT_HEADER_RE.match(line)):
                finalize(current, body_lines)
                current = None
                body_lines = []
            else:
                body_lines.append(line)

    if current is not None:
        finalize(current, body_lines)

    if not cuts:
        raise ValueError("가이드 파일에서 컷을 하나도 추출하지 못했습니다")

    return cuts


# ─── 사전 조건 ─────────────────────────────────────────────

def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        print(f"❌ {name} 바이너리를 찾을 수 없습니다. 설치 후 다시 시도하세요.")
        sys.exit(1)
    return path


def find_source_video(workspace: str) -> str:
    candidates = sorted(glob.glob(os.path.join(workspace, "sources", "*.mp4")))
    if not candidates:
        print(f"❌ sources/ 안에 mp4 파일이 없습니다: {workspace}/sources/")
        sys.exit(1)
    return candidates[0]


def find_ai_clip(workspace: str, cut_no: int) -> str | None:
    matches = sorted(glob.glob(os.path.join(workspace, "ai_clips", f"cut{cut_no}_*.mp4")))
    return matches[0] if matches else None


def find_audio_file(workspace: str, cut_no: int, mp3_hint: str) -> str | None:
    """가이드의 mp3 파일명을 우선 사용하되, 정확 매칭 실패 시
    audio/ 폴더에서 컷번호 prefix(예: `04_`)로 시작하는 mp3로 폴백."""
    direct = os.path.join(workspace, "audio", mp3_hint)
    if os.path.exists(direct):
        return direct
    prefix = f"{cut_no:02d}_"
    candidates = sorted(
        p for p in glob.glob(os.path.join(workspace, "audio", "*.mp3"))
        if os.path.basename(p).startswith(prefix)
    )
    return candidates[0] if candidates else None


# ─── ffprobe ───────────────────────────────────────────────

def probe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


# ─── ffmpeg 실행 ───────────────────────────────────────────

def run_ffmpeg(args: list[str], description: str) -> None:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ffmpeg 실패: {description}")
        print(f"   명령: {' '.join(cmd)}")
        print(f"   stderr: {result.stderr}")
        sys.exit(1)


# ─── Pass 1: 비디오 세그먼트 ───────────────────────────────

VF_COVER = (
    f"scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,"
    f"crop={CANVAS_W}:{CANVAS_H},setsar=1"
)


def build_video_segment(cut: dict, source_video: str, workspace: str, temp_dir: str) -> str:
    out_path = os.path.join(temp_dir, f"v{cut['cut_no']:02d}.mp4")
    duration = cut["timeline_duration"]

    if cut["is_ai"]:
        ai_clip = find_ai_clip(workspace, cut["cut_no"])
        if not ai_clip:
            print(f"❌ 컷 {cut['cut_no']}: AI 컷이지만 ai_clips/cut{cut['cut_no']}_*.mp4 매칭 실패")
            sys.exit(1)
        args = [
            "-ss", "0", "-t", f"{duration:.3f}",
            "-i", ai_clip,
            "-vf", VF_COVER,
            "-r", str(FPS),
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-pix_fmt", "yuv420p", "-an",
            out_path,
        ]
        label = f"AI {os.path.basename(ai_clip)}"
    else:
        args = [
            "-ss", f"{cut['source_in']:.3f}", "-to", f"{cut['source_out']:.3f}",
            "-i", source_video,
            "-vf", VF_COVER,
            "-r", str(FPS),
            "-c:v", "libx264", "-crf", "18", "-preset", "fast",
            "-pix_fmt", "yuv420p", "-an",
            out_path,
        ]
        label = f"추출 {cut['source_in']:.1f}~{cut['source_out']:.1f}s"

    run_ffmpeg(args, f"비디오 컷 {cut['cut_no']}")
    return label


# ─── Pass 2: 오디오 세그먼트 ───────────────────────────────

def build_audio_segment(cut: dict, workspace: str, temp_dir: str) -> tuple[str, float, str]:
    mp3_path = find_audio_file(workspace, cut["cut_no"], cut["mp3"])
    if not mp3_path:
        print(f"❌ 컷 {cut['cut_no']}: mp3 파일이 없습니다 (가이드: {cut['mp3']}, prefix {cut['cut_no']:02d}_도 매칭 실패)")
        sys.exit(1)

    mp3_dur = probe_duration(mp3_path)
    target = cut["timeline_duration"]
    out_path = os.path.join(temp_dir, f"a{cut['cut_no']:02d}.m4a")

    args = [
        "-i", mp3_path,
        "-af", f"apad=whole_dur={target:.3f},aresample=44100",
        "-t", f"{target:.3f}",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        out_path,
    ]
    run_ffmpeg(args, f"오디오 컷 {cut['cut_no']}")
    return out_path, mp3_dur, os.path.basename(mp3_path)


# ─── Pass 3: concat + 자막 ─────────────────────────────────

def write_concat_list(paths: list[str], list_path: str) -> None:
    with open(list_path, "w", encoding="utf-8") as f:
        for p in paths:
            # ffmpeg concat demuxer는 단일 따옴표 + 백슬래시 이스케이프 사용
            escaped = p.replace("'", r"'\''")
            f.write(f"file '{escaped}'\n")


def concat_video(video_paths: list[str], temp_dir: str) -> str:
    list_path = os.path.join(temp_dir, "v_list.txt")
    write_concat_list(video_paths, list_path)
    out = os.path.join(temp_dir, "video_all.mp4")
    run_ffmpeg(
        ["-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", out],
        "비디오 concat",
    )
    return out


def concat_audio(audio_paths: list[str], temp_dir: str) -> str:
    list_path = os.path.join(temp_dir, "a_list.txt")
    write_concat_list(audio_paths, list_path)
    out = os.path.join(temp_dir, "audio_all.m4a")
    run_ffmpeg(
        ["-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", out],
        "오디오 concat",
    )
    return out


def finalize(video_all: str, audio_all: str, workspace: str,
             output_path: str, with_subtitles: bool) -> None:
    """최종 mux. 자막 burn-in이 필요하면 ffmpeg를 workspace 디렉토리에서 실행해
    subtitle.srt를 상대경로로 참조한다 (한글 절대경로 이스케이프 회피)."""
    if with_subtitles:
        # workspace 기준 상대경로로 입력 / 출력을 변환
        v_rel = os.path.relpath(video_all, workspace)
        a_rel = os.path.relpath(audio_all, workspace)
        out_rel = os.path.relpath(output_path, workspace)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", v_rel, "-i", a_rel,
            "-vf", f"subtitles=subtitle.srt:force_style='{SUBTITLE_FORCE_STYLE}'",
            "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "-shortest",
            out_rel,
        ]
        result = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ ffmpeg 실패: 최종 mux + 자막 burn-in")
            print(f"   stderr: {result.stderr}")
            sys.exit(1)
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        run_ffmpeg(
            ["-i", video_all, "-i", audio_all,
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", "-shortest",
             output_path],
            "최종 mux",
        )


# ─── 메인 ─────────────────────────────────────────────────

def fmt_dur(seconds: float) -> str:
    return f"{seconds:.1f}s"


def fmt_size(bytes_: int) -> str:
    mb = bytes_ / (1024 * 1024)
    return f"{mb:.1f}MB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="05_edit_guide.md 기반 FFmpeg 자동 편집 (CapCut 대체)"
    )
    parser.add_argument("workspace", help="워크스페이스 폴더 경로")
    parser.add_argument("--output", "-o", default="final/final_video.mp4",
                        help="출력 경로 (workspace 기준 상대, 기본: final/final_video.mp4)")
    parser.add_argument("--no-subtitles", action="store_true",
                        help="자막 burn-in 비활성화")
    parser.add_argument("--keep-temp", action="store_true",
                        help="temp_edit/ 폴더 유지 (디버깅용)")
    parser.add_argument("--dry-run", action="store_true",
                        help="파싱 결과만 출력, ffmpeg 실행 없음")
    parser.add_argument("--guide", default="05_edit_guide.md",
                        help="가이드 파일명 (기본: 05_edit_guide.md)")
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)
    if not os.path.isdir(workspace):
        print(f"❌ 워크스페이스 폴더가 없습니다: {workspace}")
        return 1

    guide_path = os.path.join(workspace, args.guide)
    if not os.path.exists(guide_path):
        print(f"❌ 가이드 파일이 없습니다: {guide_path}")
        return 1

    require_binary("ffmpeg")
    require_binary("ffprobe")

    workspace_name = os.path.basename(workspace.rstrip("/"))
    print(f"🎬 자동 편집 시작: {workspace_name}")

    # 파싱
    print(f"📄 가이드 파싱 중...", end=" ")
    cuts = parse_edit_guide(guide_path)
    ai_count = sum(1 for c in cuts if c["is_ai"])
    normal_count = len(cuts) - ai_count
    print(f"{len(cuts)}개 컷 (일반 {normal_count} / AI {ai_count})")

    # 사전 조건
    source_video = find_source_video(workspace) if normal_count > 0 else None
    if source_video:
        print(f"   📹 소스: {os.path.relpath(source_video, workspace)}")
    if ai_count > 0:
        for c in cuts:
            if c["is_ai"]:
                clip = find_ai_clip(workspace, c["cut_no"])
                tag = os.path.basename(clip) if clip else "❌ 누락"
                print(f"   🤖 컷 {c['cut_no']}: {tag}")

    subtitle_path = os.path.join(workspace, "subtitle.srt")
    use_subs = not args.no_subtitles and os.path.exists(subtitle_path)
    if not args.no_subtitles and not os.path.exists(subtitle_path):
        print(f"   ⚠️  subtitle.srt 없음 — 자막 없이 진행")

    if args.dry_run:
        print("\n📋 [dry-run] 파싱 결과:")
        for c in cuts:
            kind = "AI" if c["is_ai"] else f"{c['source_in']:.1f}~{c['source_out']:.1f}s"
            print(f"   컷 {c['cut_no']:>2} | {c['timeline_start']:>5.1f}~{c['timeline_end']:>5.1f}s "
                  f"({c['timeline_duration']:.1f}s) | {kind:>14} | {c['mp3']}")
        return 0

    # temp 폴더
    temp_dir = os.path.join(workspace, "temp_edit")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Pass 1: 비디오
        print()
        video_paths: list[str] = []
        for i, c in enumerate(cuts, 1):
            label = build_video_segment(c, source_video, workspace, temp_dir)
            print(f"🎞 [{i}/{len(cuts)}] 컷 {c['cut_no']} "
                  f"({c['timeline_start']:.1f}~{c['timeline_end']:.1f}s) {label} ✅")
            video_paths.append(os.path.join(temp_dir, f"v{c['cut_no']:02d}.mp4"))

        # Pass 2: 오디오
        print()
        audio_paths: list[str] = []
        for i, c in enumerate(cuts, 1):
            out, mp3_dur, mp3_name = build_audio_segment(c, workspace, temp_dir)
            pad = c["timeline_duration"] - mp3_dur
            note = f"패딩 {pad:+.2f}s" if pad >= 0 else f"⚠️ {pad:.2f}s 잘림"
            print(f"🎙 [{i}/{len(cuts)}] {mp3_name} "
                  f"(mp3 {mp3_dur:.2f}s → {c['timeline_duration']:.1f}s, {note}) ✅")
            audio_paths.append(out)

        # Pass 3: concat + mux
        print()
        print("🔗 비디오 concat...", end=" ")
        video_all = concat_video(video_paths, temp_dir)
        print("✅")
        print("🔗 오디오 concat...", end=" ")
        audio_all = concat_audio(audio_paths, temp_dir)
        print("✅")

        output_path = os.path.join(workspace, args.output)
        if use_subs:
            print("📝 최종 mux + 자막 burn-in...", end=" ")
        else:
            print("📝 최종 mux...", end=" ")
        finalize(video_all, audio_all, workspace, output_path, with_subtitles=use_subs)
        print("✅")

        # 결과 요약
        final_dur = probe_duration(output_path)
        size = os.path.getsize(output_path)
        print()
        print(f"🎉 완료: {os.path.relpath(output_path)}")
        print(f"   {CANVAS_W}x{CANVAS_H} / {FPS}fps / {fmt_dur(final_dur)} / {fmt_size(size)}")

    finally:
        if not args.keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print(f"\n🗂  temp 폴더 유지: {temp_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
