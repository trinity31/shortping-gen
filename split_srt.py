#!/usr/bin/env python3
"""
SRT 자막을 4~9자 짧은 구절 단위로 재분할합니다.
음성 파일은 건드리지 않고, 컷 단위 SRT의 타이밍을 구절별로 재분배합니다.

사용법:
  python3 split_srt.py workspace/2026-04-21-이케아주방용품
  python3 split_srt.py workspace/2026-04-21-이케아주방용품 --min 4 --max 9
  python3 split_srt.py workspace/2026-04-21-이케아주방용품 --in subtitle.srt --out subtitle.srt
"""

import os
import re
import sys
import argparse


def parse_srt_time(ts: str) -> float:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = round((seconds % 1) * 1000)
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def read_srt(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        blocks = re.split(r"\n\s*\n", f.read().strip())
    entries = []
    for block in blocks:
        lines = [ln for ln in block.strip().splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        idx_line = lines[0].strip()
        time_line = lines[1].strip()
        text = " ".join(lines[2:]).strip()
        m = re.match(r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})", time_line)
        if not m:
            continue
        entries.append({
            "idx": int(idx_line) if idx_line.isdigit() else len(entries) + 1,
            "start": parse_srt_time(m.group(1)),
            "end": parse_srt_time(m.group(2)),
            "text": text,
        })
    return entries


def split_into_phrases(text: str, min_len: int = 4, max_len: int = 9) -> list[str]:
    """텍스트를 자연스러운 경계에서 4~9자 구절로 분할한다."""
    text = re.sub(r"\s+", " ", text).strip()
    # 1차: 구두점(. , ! ?) 기준으로 나누기
    rough = re.split(r"(?<=[\.,!?])\s+", text)

    phrases: list[str] = []
    for chunk in rough:
        chunk = chunk.strip()
        if not chunk:
            continue
        # 2차: 공백 기준 토큰화
        tokens = chunk.split(" ")
        current = ""
        for tok in tokens:
            # 토큰 자체가 max보다 길면 단독으로
            if len(tok) > max_len:
                if current:
                    phrases.append(current.strip())
                    current = ""
                phrases.append(tok)
                continue
            candidate = f"{current} {tok}".strip()
            if len(candidate) <= max_len:
                # 현재 버킷에 붙여도 됨
                # 단, 이미 min 이상이고 다음 토큰 붙이면 초과할 것 같으면 끊기
                current = candidate
            else:
                # 현재를 플러시
                if current:
                    phrases.append(current.strip())
                current = tok
        if current:
            phrases.append(current.strip())

    # 3차: min보다 짧은 구절은 뒤 구절과 합치기(가능하면)
    merged: list[str] = []
    for p in phrases:
        if merged and len(merged[-1]) < min_len and len(merged[-1]) + 1 + len(p) <= max_len:
            merged[-1] = f"{merged[-1]} {p}"
        else:
            merged.append(p)
    # 마지막 구절이 너무 짧으면 이전과 합치기
    if len(merged) >= 2 and len(merged[-1]) < min_len and len(merged[-2]) + 1 + len(merged[-1]) <= max_len + 2:
        merged[-2] = f"{merged[-2]} {merged[-1]}"
        merged.pop()

    return merged


def distribute_durations(phrases: list[str], start: float, end: float) -> list[tuple[float, float]]:
    """구절별 길이에 비례해 시간을 분배한다."""
    total_chars = sum(len(p) for p in phrases) or 1
    total_dur = end - start
    timings: list[tuple[float, float]] = []
    cursor = start
    for i, p in enumerate(phrases):
        if i == len(phrases) - 1:
            # 마지막은 end에 정확히 맞춤
            timings.append((cursor, end))
        else:
            dur = total_dur * (len(p) / total_chars)
            timings.append((cursor, cursor + dur))
            cursor += dur
    return timings


def split_srt(input_path: str, output_path: str, min_len: int, max_len: int) -> int:
    entries = read_srt(input_path)
    out_blocks: list[str] = []
    new_idx = 1
    for e in entries:
        phrases = split_into_phrases(e["text"], min_len=min_len, max_len=max_len)
        if not phrases:
            continue
        timings = distribute_durations(phrases, e["start"], e["end"])
        for p, (s, en) in zip(phrases, timings):
            out_blocks.append(
                f"{new_idx}\n{format_srt_time(s)} --> {format_srt_time(en)}\n{p}\n"
            )
            new_idx += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_blocks))
    return new_idx - 1


def main() -> int:
    parser = argparse.ArgumentParser(description="SRT 자막을 짧은 구절로 재분할")
    parser.add_argument("workspace", help="workspace 폴더 경로")
    parser.add_argument("--in", dest="infile", default="subtitle.srt", help="입력 SRT 파일명 (workspace 내부)")
    parser.add_argument("--out", dest="outfile", default="subtitle.srt", help="출력 SRT 파일명 (workspace 내부)")
    parser.add_argument("--min", type=int, default=4, help="최소 글자 수")
    parser.add_argument("--max", type=int, default=9, help="최대 글자 수")
    args = parser.parse_args()

    in_path = os.path.join(args.workspace, args.infile)
    out_path = os.path.join(args.workspace, args.outfile)

    if not os.path.exists(in_path):
        print(f"❌ 파일 없음: {in_path}")
        return 1

    n = split_srt(in_path, out_path, args.min, args.max)
    print(f"✅ 분할 완료: {n}개 구절")
    print(f"📝 저장: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
