# PDF 字体格式要求 - ReportLab 兼容性指南

## ⚠️ 重要：字体格式兼容性

ReportLab 对字体格式有严格要求！

### ✅ 支持的格式

**TrueType 字体 (.ttf)**
- 使用 `glyf` 表存储字形轮廓
- ReportLab 完全支持
- 文件扩展名：`.ttf`

**TrueType Collection (.ttc)**
- 包含多个 TrueType 字体的集合
- ReportLab 支持（但可能需要指定字体索引）
- 文件扩展名：`.ttc`

### ❌ 不支持的格式

**OpenType (PostScript outlines) (.otf)**
- 使用 CFF (Compact Font Format) 存储字形
- ReportLab **不支持**
- 文件扩展名：`.otf`（但有些 .otf 实际是 TrueType）

**错误示例**：
```
TTF file "fonts/NotoSerifCJKsc-Regular.otf": 
postscript outlines are not supported
```

---

## 🔍 如何判断字体格式？

### 方法 1：使用 `file` 命令

```bash
file fonts/your-font.ttf

# TrueType (支持)
your-font.ttf: TrueType Font data

# OpenType PostScript (不支持)
your-font.otf: OpenType font data
```

### 方法 2：尝试加载

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('TestFont', 'font.ttf'))
    print("✅ 支持")
except Exception as e:
    if "postscript outlines" in str(e):
        print("❌ 不支持：PostScript outlines")
    else:
        print(f"❌ 其他错误: {e}")
```

---

## 📥 推荐字体（支持上标/下标）

### 1. Noto Sans CJK SC (TrueType 版本) ⭐⭐⭐⭐⭐

**下载地址**：
- GitHub: https://github.com/googlefonts/noto-cjk/releases
- 选择: `Sans.zip` 或 `NotoSansCJKsc-*.ttf`

**特点**：
- ✅ TrueType 格式
- ✅ 完整 Unicode 支持（包括上标/下标）
- ✅ 文件大小：约 16-23 MB
- ✅ 高质量开源字体

### 2. Arial Unicode MS ⭐⭐⭐⭐

**位置**（macOS）：
- `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`

**特点**：
- ✅ TrueType 格式
- ✅ 完整 Unicode 支持
- ✅ 文件大小：22 MB
- ⚠️ 需要 Windows/macOS 系统

### 3. Source Han Sans CN (思源黑体) ⭐⭐⭐⭐

**下载地址**：
- GitHub: https://github.com/adobe-fonts/source-han-sans/releases

**特点**：
- ✅ 有 TrueType 版本
- ✅ Adobe 出品，高质量
- ✅ 完整 CJK 支持

---

## 🚫 不推荐的字体

| 字体 | 格式 | 原因 |
|------|------|------|
| NotoSerifCJKsc-Regular.otf | OTF (CFF) | ❌ ReportLab 不支持 |
| 任何 .otf (CFF) 字体 | OTF (CFF) | ❌ ReportLab 不支持 |

---

## 🔧 字体格式转换（高级）

如果必须使用 OTF 字体，可以转换为 TTF：

### 使用 FontForge

```bash
# 安装 FontForge
brew install fontforge  # macOS

# 转换字体
fontforge -lang=py -c '
import fontforge
font = fontforge.open("input.otf")
font.generate("output.ttf")
'
```

### 使用在线工具

- CloudConvert: https://cloudconvert.com/otf-to-ttf
- FontConverter: https://www.fontconverter.io/

**注意**：
- ⚠️ 转换可能丢失某些字形信息
- ⚠️ 转换后的质量可能下降
- ✅ 建议直接下载 TTF 版本

---

## 📊 Noto CJK 字体对比

| 字体 | 格式 | 大小 | ReportLab | 上标/下标 |
|------|------|------|-----------|-----------|
| NotoSansCJKsc-Regular.otf | OTF (CFF) | 16 MB | ❌ | - |
| NotoSerifCJKsc-Regular.otf | OTF (CFF) | 23 MB | ❌ | - |
| NotoSansCJKsc-Regular.ttf | TTF (glyf) | 16-20 MB | ✅ | ❓ 需测试 |
| NotoSansSC-Regular.ttf | TTF (glyf) | 10 MB | ✅ | ❌ 已知问题 |

---

## 🎯 推荐操作流程

### 步骤 1：下载正确格式的字体

访问：https://github.com/googlefonts/noto-cjk/releases

下载其中之一：
- `NotoSansCJKsc-Regular.ttf` (TrueType 版本)
- 或下载 `Sans.zip` 并解压

### 步骤 2：验证格式

```bash
file fonts/NotoSansCJKsc-Regular.ttf
# 应该显示: TrueType Font data
```

### 步骤 3：测试字体

```bash
cd /Users/enithz/Desktop/pdfnew
source venv/bin/activate
python test_font.py
```

### 步骤 4：如果测试通过

我会帮您：
1. 提交新字体到 Git
2. 更新配置
3. 推送到 GitHub
4. 在 Zeabur 上测试

---

## 💡 关键点

1. **不是所有 .otf 文件都是 PostScript outlines**
   - 有些 .otf 实际是 TrueType 格式
   - 需要用 `file` 命令检查

2. **ReportLab 的限制**
   - 这是库本身的限制，不是配置问题
   - 必须使用 TrueType 格式

3. **文件扩展名不可靠**
   - `.ttf` 通常是 TrueType
   - `.otf` 可能是 TrueType 或 PostScript
   - 需要检查实际格式

---

## 📦 当前字体文件状态

```
✅ Arial-Unicode.ttf (22MB) - TrueType, 本地开发可用
✅ NotoSansSC-Regular.ttf (10MB) - TrueType, 但上标/下标有问题
❌ NotoSerifCJKsc-Regular.otf (23MB) - PostScript, ReportLab 不支持
```

---

## 🎯 下一步

请您：
1. 下载 **TrueType 格式** 的 Noto Sans CJK SC
2. 替换当前的 .otf 文件
3. 告诉我完成，我会帮您测试和部署

推荐下载链接：
https://github.com/googlefonts/noto-cjk/releases
