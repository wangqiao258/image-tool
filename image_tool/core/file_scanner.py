"""Scan a folder for image files. Independent module - no GUI dependency."""

from pathlib import Path
from typing import List

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def scan_images(folder: str | Path, extensions: set[str] | None = None) -> List[Path]:
    """
    Scan a folder for image files (non-recursive).

    Args:
        folder: Path to the folder to scan.
        extensions: Set of allowed extensions (e.g. {'.jpg', '.png'}).
                    Defaults to SUPPORTED_EXTENSIONS.

    Returns:
        Sorted list of image file paths.

    Raises:
        FileNotFoundError: If folder does not exist.
        NotADirectoryError: If path is not a directory.
    """
    folder = Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {folder}")

    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS

    extensions = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}

    images = [
        f for f in sorted(folder.iterdir())
        if f.is_file() and f.suffix.lower() in extensions
    ]
    return images
