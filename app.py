"""
批量图片处理工具 - 入口文件
功能：批量改尺寸、自动重命名、加出血线

用法：
    python app.py
"""

import sys
from pathlib import Path

# Ensure the project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("Pillow")

    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        sys.exit(1)


def main():
    check_dependencies()

    from image_tool.gui.main_window import MainWindow
    MainWindow.launch()


if __name__ == "__main__":
    main()
