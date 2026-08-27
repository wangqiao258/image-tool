"""Batch rename images. Independent module - no dependencies."""

from pathlib import Path


def generate_name(
    prefix: str,
    index: int,
    original_ext: str,
    digits: int = 3,
) -> str:
    """
    Generate a new filename with prefix and padded index.

    Args:
        prefix: Name prefix (e.g. 'product').
        index: Numeric index (will be zero-padded).
        original_ext: Original file extension including dot (e.g. '.jpg').
        digits: Minimum number of digits for zero-padding (default 3).

    Returns:
        New filename string, e.g. 'product_001.jpg'.
    """
    if not original_ext.startswith("."):
        original_ext = f".{original_ext}"
    ext = original_ext.lower()
    return f"{prefix}_{str(index).zfill(digits)}{ext}"


def batch_rename(
    files: list,
    prefix: str,
    start_index: int = 1,
    digits: int = 3,
) -> list:
    """
    Generate rename mapping for a list of files.

    Returns:
        List of (original_path, new_filename) tuples.
    """
    mapping = []
    for i, f in enumerate(files, start=start_index):
        new_name = generate_name(prefix, i, f.suffix, digits)
        mapping.append((f, new_name))
    return mapping
