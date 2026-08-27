"""Add bleed lines to images. Independent module - only depends on Pillow."""

from PIL import Image, ImageDraw

# Conversion: mm to pixels at 72 DPI
MM_TO_PX = 72 / 25.4  # ~2.835 px/mm


def add_bleed(
    img: Image.Image,
    bleed_mm: float,
    color: str = "white",
) -> Image.Image:
    """
    Add bleed area around an image by expanding the canvas.

    Args:
        img: A PIL Image object.
        bleed_mm: Bleed width in millimeters (applied to all four sides).
        color: Fill color for the bleed area (default: 'white').

    Returns:
        A new PIL Image with bleed area added (original is not modified).
    """
    if bleed_mm < 0:
        raise ValueError(f"出血宽度不能为负数: {bleed_mm}")
    if bleed_mm == 0:
        return img.copy()

    bleed_px = int(bleed_mm * MM_TO_PX)
    new_width = img.width + bleed_px * 2
    new_height = img.height + bleed_px * 2

    if img.mode in ("RGBA", "LA", "PA"):
        canvas = Image.new(img.mode, (new_width, new_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        _draw_bleed_rect(draw, new_width, new_height, bleed_px, img.width, img.height, color)
    else:
        try:
            canvas = Image.new(img.mode, (new_width, new_height), color)
        except ValueError:
            canvas = Image.new("RGB", (new_width, new_height), color)
            img = img.convert("RGB")

    canvas.paste(img, (bleed_px, bleed_px))
    return canvas


def _draw_bleed_rect(draw, canvas_w, canvas_h, bleed_px, orig_w, orig_h, color):
    """Draw colored rectangles for the bleed area on transparent images."""
    draw.rectangle([(0, 0), (canvas_w, bleed_px)], fill=color)
    draw.rectangle([(0, bleed_px + orig_h), (canvas_w, canvas_h)], fill=color)
    draw.rectangle([(0, bleed_px), (bleed_px, bleed_px + orig_h)], fill=color)
    draw.rectangle([(bleed_px + orig_w, bleed_px), (canvas_w, bleed_px + orig_h)], fill=color)


def add_bleed_marks(
    img: Image.Image,
    bleed_mm: float,
    mark_length_mm: float = 3.0,
    mark_offset_mm: float = 0.5,
    mark_color: str = "black",
) -> Image.Image:
    """
    Add crop marks at the corners of the original content area.
    Should be called on an image that already has bleed added.
    """
    bleed_px = int(bleed_mm * MM_TO_PX)
    length_px = int(mark_length_mm * MM_TO_PX)
    offset_px = int(mark_offset_mm * MM_TO_PX)

    result = img.copy()
    draw = ImageDraw.Draw(result)

    cx0, cy0 = bleed_px, bleed_px
    cx1 = img.width - bleed_px
    cy1 = img.height - bleed_px

    corners = [
        # Top-left
        ((cx0 - offset_px - length_px, cy0), (cx0 - offset_px, cy0),
         (cx0, cy0 - offset_px - length_px), (cx0, cy0 - offset_px)),
        # Top-right
        ((cx1 + offset_px, cy0), (cx1 + offset_px + length_px, cy0),
         (cx1, cy0 - offset_px - length_px), (cx1, cy0 - offset_px)),
        # Bottom-left
        ((cx0 - offset_px - length_px, cy1), (cx0 - offset_px, cy1),
         (cx0, cy1 + offset_px), (cx0, cy1 + offset_px + length_px)),
        # Bottom-right
        ((cx1 + offset_px, cy1), (cx1 + offset_px + length_px, cy1),
         (cx1, cy1 + offset_px), (cx1, cy1 + offset_px + length_px)),
    ]

    for h_start, h_end, v_start, v_end in corners:
        draw.line([h_start, h_end], fill=mark_color, width=1)
        draw.line([v_start, v_end], fill=mark_color, width=1)

    return result
