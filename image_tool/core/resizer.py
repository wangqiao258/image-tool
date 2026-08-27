"""Resize images. Independent module - only depends on Pillow."""

from PIL import Image


def resize(
    img: Image.Image,
    target_width: float,
    target_height: float,
    unit: str = "px",
    dpi: int = 72,
) -> Image.Image:
    """
    Resize an image to exact specified dimensions.

    Args:
        img: A PIL Image object.
        target_width: Desired width.
        target_height: Desired height.
        unit: One of 'px' (pixels), 'cm' (centimeters), 'mm' (millimeters).
        dpi: Dots per inch for physical unit conversion (default 72).

    Returns:
        A new resized PIL Image (original is not modified).
    """
    if target_width <= 0 or target_height <= 0:
        raise ValueError(f"尺寸必须大于零: {target_width}x{target_height}")

    unit = unit.lower()
    if unit == "cm":
        scale = dpi / 2.54
    elif unit == "mm":
        scale = dpi / 25.4
    elif unit == "px":
        scale = 1
    else:
        raise ValueError(f"不支持的单位: {unit}（支持 px, cm, mm）")

    width_px = int(target_width * scale)
    height_px = int(target_height * scale)

    resized = img.resize((width_px, height_px), Image.Resampling.LANCZOS)
    return resized


def resize_by_percent(
    img: Image.Image,
    percent: float,
) -> Image.Image:
    """
    Resize an image by percentage, preserving aspect ratio.

    Args:
        img: A PIL Image object.
        percent: Scale percentage (e.g. 50 = half size, 200 = double size).

    Returns:
        A new resized PIL Image (original is not modified).
    """
    if percent <= 0:
        raise ValueError(f"缩放比例必须大于零: {percent}")

    scale = percent / 100.0
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)

    # Ensure minimum 1px
    new_width = max(1, new_width)
    new_height = max(1, new_height)

    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized
