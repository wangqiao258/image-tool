# 批量图片处理工具

带图形界面的批量图片处理工具，适合不懂技术的同事使用。设计师每次上新要处理几百张商品图：统一尺寸 → 按规则命名 → 加 3mm 出血线，手工做要几小时。

## 功能

- **📐 改尺寸** — 批量调整图片尺寸（支持像素 px、厘米 cm、毫米 mm）
- **📝 自动重命名** — 自定义前缀 + 序号，自动递增（如 `产品_001.jpg`）
- **📐 加出血线** — 四周扩展出血区域，支持自定义宽度和颜色

每个功能可以独立开关，按需使用。

## 安装依赖

```bash
pip install Pillow
```

## 使用方法

```bash
cd image_tool
python app.py
```

1. 选择 **输入文件夹**（包含要处理的图片）
2. 选择 **输出文件夹**（处理后的图片保存位置）
3. 勾选需要的功能，设置参数
4. 点击 **开始处理**

## 支持的图片格式

读取：JPG、PNG、BMP、TIFF、WebP
输出：保持原格式（JPG/PNG 质量优化）

## 项目结构

```
image_tool/
├── app.py                  # 入口文件
├── gui/                    # 界面模块
│   ├── main_window.py      # 主窗口
│   ├── widgets.py          # 可复用组件
│   └── dialogs.py          # 弹窗提示
├── core/                   # 核心功能（可独立使用）
│   ├── file_scanner.py     # 扫描图片文件
│   ├── resizer.py          # 图片缩放
│   ├── bleeder.py          # 加出血线
│   └── renamer.py          # 批量重命名
└── README.md
```

## 独立使用 Core 模块

每个 core 模块可以被其他 Python 代码直接调用：

```python
from core import scan_images, resize, add_bleed, generate_name
from PIL import Image

# 扫描文件夹
images = scan_images("/path/to/folder")

# 缩放图片
img = Image.open(images[0])
resized = resize(img, 1920, 1080, unit="px")

# 加出血线
with_bleed = add_bleed(resized, bleed_mm=3, color="white")

# 重命名
new_name = generate_name("产品", 1, ".jpg")  # -> "产品_001.jpg"
```
