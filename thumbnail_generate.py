#!/usr/bin/env python3
"""
숏핑 썸네일 자동 생성기
업로드_정보.md에서 문구를 추출하고 제품 이미지와 합성하여 썸네일을 만듭니다.

사용법:
  python3 thumbnail_generate.py workspace/2026-04-09_직장인활력건강템
  python3 thumbnail_generate.py workspace/2026-04-09_직장인활력건강템 --line1 "직장인 건강 꿀템" --line2 "이 3개면 달라짐"
  python3 thumbnail_generate.py workspace/2026-04-09_직장인활력건강템 --accent "#FF4444"
"""

import os
import re
import sys
import math
import argparse
from PIL import Image, ImageDraw, ImageFont

# ─── 설정 ────────────────────────────────────────────────

CANVAS_W = 1080
CANVAS_H = 1920
BORDER_WIDTH = 16
SECTION_BG = ["#FFF9C4", "#E3F2FD", "#F3E5F5"]
DEFAULT_ACCENT = "#FFD600"
DEFAULT_BORDER = "#FFD600"
ROTATION_DEG = 0
IMAGE_ZOOM = 1.0

# 시스템 폰트 후보 (macOS)
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/AppleSDGothicNeo-Bold.otf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleSDGothicNeo-Bold.otf",
    "/System/Library/Fonts/Helvetica.ttc",
]


# ─── 유틸 ────────────────────────────────────────────────

def find_font(size: int) -> ImageFont.FreeTypeFont:
    """시스템에서 사용 가능한 한글 폰트를 찾습니다."""
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def parse_thumbnail_text(upload_info_path: str) -> list[str]:
    """업로드_정보.md에서 추천 썸네일 문구를 추출합니다."""
    with open(upload_info_path, "r", encoding="utf-8") as f:
        content = f.read()

    # "1 (추천)" 행에서 문구 추출
    match = re.search(r"\|\s*1\s*\(추천\)\s*\|\s*\*\*(.+?)\*\*\s*/\s*\*\*(.+?)\*\*", content)
    if match:
        return [match.group(1).strip(), match.group(2).strip()]

    # 폴백: 첫 번째 행
    match = re.search(r"\|\s*\d\s*\|?\s*\*\*(.+?)\*\*\s*/\s*\*\*(.+?)\*\*", content)
    if match:
        return [match.group(1).strip(), match.group(2).strip()]

    return ["꿀템 추천", "지금 바로 확인"]


def find_product_images(workspace: str) -> list[str]:
    """workspace/product_images/ 폴더에서 제품 이미지를 번호순으로 찾습니다."""
    images_dir = os.path.join(workspace, "product_images")

    # 폴더 없으면 생성
    if not os.path.exists(images_dir):
        os.makedirs(images_dir, exist_ok=True)
        return []

    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = []
    for f in sorted(os.listdir(images_dir)):
        if os.path.splitext(f)[1].lower() in extensions:
            images.append(os.path.join(images_dir, f))

    return images[:3]  # 최대 3개


# ─── 썸네일 생성 ─────────────────────────────────────────

def crop_middle_half(img: Image.Image) -> Image.Image:
    """세로 이미지(9:16)의 가운데 절반을 크롭합니다."""
    quarter_h = img.height // 4
    return img.crop((0, quarter_h, img.width, quarter_h * 3))


def draw_image_contain(canvas: Image.Image, img: Image.Image,
                       x: int, y: int, w: int, h: int,
                       bg_color: str = "#FFFFFF"):
    """이미지 전체가 보이도록 캔버스에 맞춰 배치합니다.
    이미지가 잘리지 않고 전체가 표시되며, 여백은 bg_color로 채웁니다."""
    img_ratio = img.width / img.height
    area_ratio = w / h

    if img_ratio > area_ratio:
        # 이미지가 더 넓음 → 너비에 맞추기
        new_w = w
        new_h = int(w / img_ratio)
    else:
        # 이미지가 더 높음 → 높이에 맞추기
        new_h = h
        new_w = int(h * img_ratio)

    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # 중앙 정렬
    paste_x = x + (w - new_w) // 2
    paste_y = y + (h - new_h) // 2

    canvas.paste(resized, (paste_x, paste_y))


def draw_gradient_overlay(draw: ImageDraw.ImageDraw,
                          x: int, y: int, w: int, h: int):
    """이미지 위에 어두운 그라데이션 오버레이를 그립니다."""
    for i in range(h):
        # 중앙에서 어두워지는 그라데이션
        ratio = i / h
        # 상단/하단에서 더 어둡게
        alpha = int(90 + 60 * (1 - abs(ratio - 0.5) * 2))
        draw.rectangle([x, y + i, x + w, y + i + 1],
                       fill=(0, 0, 0, alpha))


def draw_text_with_stroke(draw: ImageDraw.ImageDraw,
                          text: str, position: tuple,
                          font: ImageFont.FreeTypeFont,
                          fill: str, anchor: str = "mm"):
    """굵은 검정 테두리 + 색상 채우기 텍스트를 그립니다."""
    x, y = position

    # 1패스: 검정 테두리 (얇게)
    draw.text((x, y), text, font=font, fill=fill,
              anchor=anchor, stroke_width=14, stroke_fill="black")

    # 2패스: 최종 색상 채우기
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def generate_thumbnail(
    lines: list[str],
    product_images: list[str],
    output_path: str,
    accent_color: str = DEFAULT_ACCENT,
    border_color: str = DEFAULT_BORDER,
    no_images: bool = False,
):
    """썸네일 이미지를 생성합니다."""

    # 캔버스 생성 (RGBA)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), "white")

    num_sections = min(len(product_images), 3) if not no_images and product_images else 1
    section_h = CANVAS_H // max(num_sections, 1)

    # 섹션별 이미지 배치 (테두리/구분선 없이 풀사이즈)
    for i in range(max(num_sections, 1)):
        sy = i * section_h
        sh = section_h

        # 제품 이미지
        if not no_images and i < len(product_images):
            try:
                img = Image.open(product_images[i]).convert("RGBA")
                draw_image_contain(canvas, img, 0, sy, CANVAS_W, sh)
            except Exception as e:
                print(f"   ⚠️ 이미지 로드 실패: {product_images[i]} ({e})")
        else:
            # 이미지 없으면 파스텔 배경
            section_canvas = Image.new("RGBA", (CANVAS_W, sh), SECTION_BG[i % 3])
            canvas.paste(section_canvas, (0, sy))

    # 텍스트 레이어 (--no-text가 아닌 경우에만)
    if lines and lines[0]:
        font_size = int(min(160, CANVAS_W * 0.15))
        font = find_font(font_size)

        # 그라데이션 오버레이 (텍스트 가독성)
        overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        draw_gradient_overlay(overlay_draw, 0, 0, CANVAS_W, CANVAS_H)
        canvas = Image.alpha_composite(canvas, overlay)

        text_layer = Image.new("RGBA", (CANVAS_W * 2, CANVAS_H * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)

        center_x = CANVAS_W
        center_y = CANVAS_H
        line_spacing = int(font_size * 1.4)

        total_text_h = len(lines) * line_spacing
        start_y = center_y - total_text_h // 2

        for i, line in enumerate(lines):
            ly = start_y + i * line_spacing
            if len(lines) <= 2:
                color = "white" if i == 0 else accent_color
            else:
                color = accent_color if 0 < i < len(lines) - 1 else "white"
            draw_text_with_stroke(text_draw, line, (center_x, ly), font, color)

        text_layer = text_layer.rotate(ROTATION_DEG, resample=Image.BICUBIC,
                                        expand=False, center=(center_x, center_y))

        crop_x = (text_layer.width - CANVAS_W) // 2
        crop_y = (text_layer.height - CANVAS_H) // 2
        text_cropped = text_layer.crop(
            (crop_x, crop_y, crop_x + CANVAS_W, crop_y + CANVAS_H)
        )
        canvas = Image.alpha_composite(canvas, text_cropped)

    # PNG로 저장
    canvas.convert("RGB").save(output_path, "PNG", quality=95)
    return output_path


# ─── 메인 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="숏핑 썸네일 자동 생성기 — 업로드_정보.md + 제품 이미지 → thumbnail.png",
    )
    parser.add_argument(
        "workspace",
        help="작업 폴더 경로 (예: workspace/2026-04-09_직장인활력건강템)",
    )
    parser.add_argument(
        "--line1",
        help="썸네일 첫째 줄 문구 (미지정 시 업로드_정보.md에서 추출)",
    )
    parser.add_argument(
        "--line2",
        help="썸네일 둘째 줄 문구",
    )
    parser.add_argument(
        "--line3",
        help="썸네일 셋째 줄 문구 (선택)",
    )
    parser.add_argument(
        "--accent",
        default=DEFAULT_ACCENT,
        help=f"강조 텍스트 색상 (기본: {DEFAULT_ACCENT})",
    )
    parser.add_argument(
        "--border",
        default=DEFAULT_BORDER,
        help=f"테두리 색상 (기본: {DEFAULT_BORDER})",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="제품 이미지 없이 배경 그라데이션만 사용",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="텍스트 없이 이미지만으로 생성",
    )

    args = parser.parse_args()

    # 경로 확인
    if not os.path.exists(args.workspace):
        print(f"❌ 작업 폴더를 찾을 수 없습니다: {args.workspace}")
        sys.exit(1)

    # 썸네일 문구 결정
    if args.no_text:
        lines = []
        print("📌 텍스트 없이 이미지만으로 생성")
    elif args.line1:
        lines = [args.line1]
        if args.line2:
            lines.append(args.line2)
        if args.line3:
            lines.append(args.line3)
    else:
        upload_info = os.path.join(args.workspace, "업로드_정보.md")
        if os.path.exists(upload_info):
            lines = parse_thumbnail_text(upload_info)
            print(f"📝 업로드_정보.md에서 문구 추출: {lines}")
        else:
            print("❌ 업로드_정보.md가 없고 --line1도 미지정")
            sys.exit(1)

    # 제품 이미지 찾기
    product_images = find_product_images(args.workspace)
    if product_images:
        print(f"🖼  제품 이미지 {len(product_images)}개 발견:")
        for img in product_images:
            print(f"   - {os.path.basename(img)}")
    else:
        print("📌 제품 이미지 없음 → 배경 그라데이션으로 생성")
        print(f"   (이미지를 사용하려면 {args.workspace}/product_images/ 폴더에 넣어주세요)")
        print(f"   파일명 예: 1_멀티비타민.jpg, 2_아이마스크.jpg, 3_마사지기.jpg")

    # 썸네일 생성
    output_path = os.path.join(args.workspace, "thumbnail.png")

    print(f"\n🎨 썸네일 생성 중...")
    print(f"   문구: {' / '.join(lines)}")
    print(f"   강조색: {args.accent}")
    print(f"   테두리: {args.border}")

    generate_thumbnail(
        lines=lines,
        product_images=product_images,
        output_path=output_path,
        accent_color=args.accent,
        border_color=args.border,
        no_images=args.no_images or not product_images,
    )

    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✅ 썸네일 저장: {output_path} ({size_kb:.0f}KB)")
    print(f"   크기: {CANVAS_W}x{CANVAS_H}")


if __name__ == "__main__":
    main()
