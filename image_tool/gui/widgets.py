"""Reusable GUI components."""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path


class FolderPicker(ttk.Frame):
    """A folder selection widget with label, entry, and browse button."""

    def __init__(self, parent, label: str = "选择文件夹", **kwargs):
        super().__init__(parent, **kwargs)

        self._var = tk.StringVar()

        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))

        self._entry = ttk.Entry(self, textvariable=self._var, width=40)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self._btn = ttk.Button(self, text="浏览...", command=self._browse)
        self._btn.pack(side=tk.LEFT)

    def _browse(self):
        folder = filedialog.askdirectory(title=self._entry.cget("text") or "选择文件夹")
        if folder:
            self._var.set(folder)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str):
        self._var.set(value)


class LabeledEntry(ttk.Frame):
    """A labeled text entry widget."""

    def __init__(self, parent, label: str, default: str = "", width: int = 10, **kwargs):
        super().__init__(parent, **kwargs)

        self._var = tk.StringVar(value=default)

        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))

        self._entry = ttk.Entry(self, textvariable=self._var, width=width)
        self._entry.pack(side=tk.LEFT)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str):
        self._var.set(value)


class FeatureSection(ttk.LabelFrame):
    """A labeled section with an enable checkbox, used for each feature."""

    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, text=title, **kwargs)

        self._enabled = tk.BooleanVar(value=False)

        self._checkbox = ttk.Checkbutton(
            self, text="启用", variable=self._enabled
        )
        self._checkbox.pack(anchor=tk.W, padx=5, pady=2)

        # Content frame for feature-specific controls
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

    @property
    def enabled(self) -> bool:
        return self._enabled.get()

    def set_enabled(self, value: bool):
        self._enabled.set(value)
