"""Main application window with all feature sections."""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image
import threading
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .widgets import FolderPicker, LabeledEntry, FeatureSection
from .dialogs import show_error, show_info, show_warning, show_completion
from image_tool.core.file_scanner import scan_images
from image_tool.core.resizer import resize, resize_by_percent
from image_tool.core.bleeder import add_bleed
from image_tool.core.renamer import generate_name

# Max parallel workers (leave 1 core free for OS/GUI)
MAX_WORKERS = max(1, os.cpu_count() - 1)


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("批量图片处理工具")
        self.root.geometry("700x680")
        self.root.resizable(True, True)
        self.root.minsize(650, 600)
        self._processing = False
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        folder_frame = ttk.LabelFrame(main_frame, text="文件夹设置", padding=5)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        self.input_picker = FolderPicker(folder_frame, label="输入文件夹")
        self.input_picker.pack(fill=tk.X, pady=2)
        self.output_picker = FolderPicker(folder_frame, label="输出文件夹")
        self.output_picker.pack(fill=tk.X, pady=2)

        self._build_resize_section(main_frame)
        self._build_rename_section(main_frame)
        self._build_bleed_section(main_frame)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        self._progress_var = tk.DoubleVar(value=0)
        self._status_var = tk.StringVar(value="就绪")
        self.progress_bar = ttk.Progressbar(btn_frame, variable=self._progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.status_label = ttk.Label(btn_frame, textvariable=self._status_var)
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))
        self.start_btn = ttk.Button(btn_frame, text="开始处理", command=self._on_start, width=15)
        self.start_btn.pack(side=tk.RIGHT)

    def _build_resize_section(self, parent):
        section = FeatureSection(parent, title="📐 改尺寸")
        section.pack(fill=tk.X, pady=(0, 5))
        self.resize_section = section

        mode_row = ttk.Frame(section.content)
        mode_row.pack(fill=tk.X, pady=(0, 5))
        self._resize_mode = tk.StringVar(value="exact")
        ttk.Radiobutton(
            mode_row, text="精确尺寸", variable=self._resize_mode, value="exact",
            command=self._on_resize_mode_change
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            mode_row, text="按比例缩放", variable=self._resize_mode, value="percent",
            command=self._on_resize_mode_change
        ).pack(side=tk.LEFT)

        # Exact size controls
        self._exact_frame = ttk.Frame(section.content)
        self._exact_frame.pack(fill=tk.X)
        self.resize_w = LabeledEntry(self._exact_frame, label="宽度", default="1920", width=10)
        self.resize_w.pack(side=tk.LEFT, padx=(0, 10))
        self.resize_h = LabeledEntry(self._exact_frame, label="高度", default="1080", width=10)
        self.resize_h.pack(side=tk.LEFT, padx=(0, 10))
        self._unit_var = tk.StringVar(value="px")
        unit_frame = ttk.Frame(self._exact_frame)
        unit_frame.pack(side=tk.LEFT)
        ttk.Label(unit_frame, text="单位:").pack(side=tk.LEFT, padx=(10, 5))
        for val in ["px", "cm", "mm"]:
            ttk.Radiobutton(unit_frame, text=val, variable=self._unit_var, value=val).pack(side=tk.LEFT)

        # Percentage controls (hidden by default)
        self._percent_frame = ttk.Frame(section.content)
        self.resize_percent = LabeledEntry(
            self._percent_frame, label="缩放比例 (%)", default="50", width=8
        )
        self.resize_percent.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(self._percent_frame, text="(50 = 缩小一半, 200 = 放大一倍)").pack(side=tk.LEFT)

    def _on_resize_mode_change(self):
        if self._resize_mode.get() == "exact":
            self._percent_frame.pack_forget()
            self._exact_frame.pack(fill=tk.X)
        else:
            self._exact_frame.pack_forget()
            self._percent_frame.pack(fill=tk.X)

    def _build_rename_section(self, parent):
        section = FeatureSection(parent, title="📝 自动重命名")
        section.pack(fill=tk.X, pady=(0, 5))
        self.rename_section = section
        row = ttk.Frame(section.content)
        row.pack(fill=tk.X)
        self.rename_prefix = LabeledEntry(row, label="前缀", default="图片", width=15)
        self.rename_prefix.pack(side=tk.LEFT, padx=(0, 10))
        self.rename_start = LabeledEntry(row, label="起始编号", default="1", width=6)
        self.rename_start.pack(side=tk.LEFT, padx=(0, 10))
        self.rename_digits = LabeledEntry(row, label="位数", default="3", width=4)
        self.rename_digits.pack(side=tk.LEFT)
        ttk.Label(row, text="(如: 图片_001.jpg)").pack(side=tk.LEFT, padx=10)

    def _build_bleed_section(self, parent):
        section = FeatureSection(parent, title="📐 加出血线")
        section.pack(fill=tk.X, pady=(0, 5))
        self.bleed_section = section
        row = ttk.Frame(section.content)
        row.pack(fill=tk.X)
        self.bleed_width = LabeledEntry(row, label="出血宽度 (mm)", default="3", width=6)
        self.bleed_width.pack(side=tk.LEFT, padx=(0, 10))
        self._bleed_color_var = tk.StringVar(value="white")
        color_frame = ttk.Frame(row)
        color_frame.pack(side=tk.LEFT)
        ttk.Label(color_frame, text="颜色:").pack(side=tk.LEFT, padx=(10, 5))
        for val, label in [("white", "白"), ("black", "黑"), ("red", "红"), ("blue", "蓝")]:
            ttk.Radiobutton(color_frame, text=label, variable=self._bleed_color_var, value=val).pack(side=tk.LEFT)

    # ── Collect settings before background thread (read on main thread) ──

    def _collect_settings(self):
        """Snapshot all GUI values into a dict (must be called on main thread)."""
        settings = {}
        # Resize
        settings["resize_enabled"] = self.resize_section.enabled
        settings["resize_mode"] = self._resize_mode.get()
        settings["resize_w"] = float(self.resize_w.get())
        settings["resize_h"] = float(self.resize_h.get())
        settings["resize_unit"] = self._unit_var.get()
        settings["resize_percent"] = float(self.resize_percent.get())
        # Bleed
        settings["bleed_enabled"] = self.bleed_section.enabled
        settings["bleed_mm"] = float(self.bleed_width.get())
        settings["bleed_color"] = self._bleed_color_var.get()
        # Rename
        settings["rename_enabled"] = self.rename_section.enabled
        settings["rename_prefix"] = self.rename_prefix.get()
        settings["rename_start"] = int(self.rename_start.get())
        settings["rename_digits"] = int(self.rename_digits.get())
        return settings

    # ── Start processing ──

    def _on_start(self):
        input_folder = self.input_picker.get()
        output_folder = self.output_picker.get()
        if not input_folder:
            show_error("错误", "请先选择输入文件夹！")
            return
        if not output_folder:
            show_error("错误", "请先选择输出文件夹！")
            return
        if not any([self.resize_section.enabled, self.rename_section.enabled, self.bleed_section.enabled]):
            show_warning("提示", "请至少启用一个功能（改尺寸/重命名/加出血线）")
            return
        try:
            images = scan_images(input_folder)
        except (FileNotFoundError, NotADirectoryError) as e:
            show_error("错误", str(e))
            return
        if not images:
            show_warning("提示", "输入文件夹中没有找到支持的图片文件！\n支持格式: JPG, PNG, BMP, TIFF, WebP")
            return

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        # Snapshot settings on main thread, then hand off to background
        settings = self._collect_settings()
        self._processing = True
        self.start_btn.config(state=tk.DISABLED)
        self._progress_var.set(0)
        self._status_var.set("准备中...")

        thread = threading.Thread(
            target=self._process_images,
            args=(images, output_folder, settings),
            daemon=True,
        )
        thread.start()

    # ── Background processing ──

    def _process_images(self, images, output_folder, settings):
        """Run in background thread. Uses ThreadPoolExecutor for parallelism."""
        total = len(images)
        errors = []
        done_count = 0

        def update_progress(filename, count):
            """Thread-safe GUI update via root.after()."""
            self.root.after(0, self._progress_var.set, count / total * 100)
            self.root.after(0, self._status_var.set, f"处理中: {filename} ({count}/{total})")

        def process_one(img_path, index):
            """Process a single image. Runs in worker thread."""
            img = Image.open(img_path)

            if settings["resize_enabled"]:
                if settings["resize_mode"] == "percent":
                    img = resize_by_percent(img, settings["resize_percent"])
                else:
                    img = resize(img, settings["resize_w"], settings["resize_h"], settings["resize_unit"])

            if settings["bleed_enabled"]:
                img = add_bleed(img, settings["bleed_mm"], settings["bleed_color"])

            if settings["rename_enabled"]:
                new_name = generate_name(
                    settings["rename_prefix"],
                    settings["rename_start"] + index,
                    img_path.suffix,
                    settings["rename_digits"],
                )
            else:
                new_name = img_path.name

            out_path = Path(output_folder) / new_name
            save_kwargs = {}
            if out_path.suffix.lower() in (".jpg", ".jpeg"):
                save_kwargs["quality"] = 95
            elif out_path.suffix.lower() == ".png":
                save_kwargs["optimize"] = True

            img.save(str(out_path), **save_kwargs)
            img.close()
            return new_name

        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(process_one, img_path, i): img_path
                for i, img_path in enumerate(images)
            }

            for future in as_completed(futures):
                img_path = futures[future]
                done_count += 1
                try:
                    future.result()
                except Exception as e:
                    errors.append(f"{img_path.name}: {e}")

                # Update GUI (thread-safe)
                update_progress(img_path.name, done_count)

        # Done — back to main thread
        self.root.after(0, self._on_processing_done, total, errors)

    def _on_processing_done(self, total, errors):
        """Called on main thread when all processing is complete."""
        self._processing = False
        self.start_btn.config(state=tk.NORMAL)
        self._status_var.set(f"完成！共 {total} 张，失败 {len(errors)} 张")
        show_completion("处理完成", total, errors)

    @staticmethod
    def launch():
        root = tk.Tk()
        MainWindow(root)
        root.mainloop()
