"""Dialog windows for errors, confirmations, and status."""

import tkinter as tk
from tkinter import messagebox


def show_error(title: str, message: str):
    """Show an error dialog."""
    messagebox.showerror(title, message)


def show_info(title: str, message: str):
    """Show an information dialog."""
    messagebox.showinfo(title, message)


def show_warning(title: str, message: str):
    """Show a warning dialog."""
    messagebox.showwarning(title, message)


def show_completion(title: str, total: int, errors: list = None):
    """Show a completion dialog with summary."""
    msg = f"处理完成！\n\n共处理 {total} 张图片。"
    if errors:
        msg += f"\n\n有 {len(errors)} 张处理失败："
        for err in errors[:5]:
            msg += f"\n  • {err}"
        if len(errors) > 5:
            msg += f"\n  ...还有 {len(errors) - 5} 张"
    messagebox.showinfo(title, msg)
