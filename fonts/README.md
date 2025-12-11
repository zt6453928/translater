# PDF 字体配置

这个目录用于存放 PDF 生成所需的字体文件，以确保中文和数学符号正确显示。

## 📋 当前状态

✅ **本地开发可用**：已配置使用系统的 Arial Unicode 字体（通过符号链接）  
⚠️ **Zeabur 部署需要**：手动下载并上传 Noto Sans CJK SC 字体

## 🎯 推荐字体

为了确保 PDF 生成时中文和数学符号正确显示，请添加以下字体文件之一：

### 1. Noto Sans CJK SC (强烈推荐)
- **文件名**: `NotoSansCJKsc-Regular.otf` 或 `NotoSansSC-Regular.ttf`
- **下载**: https://fonts.google.com/noto/specimen/Noto+Sans+SC
- **备用**: https://github.com/googlefonts/noto-cjk/releases
- **特点**: 完整的简体中文支持，包含数学符号，文件大小约 16 MB
- **最佳用途**: 生产环境部署

### 2. Arial Unicode (已配置)
- **文件名**: `Arial-Unicode.ttf` (符号链接)
- **位置**: 系统字体 `/System/Library/Fonts/Supplemental/Arial Unicode.ttf`
- **特点**: macOS 系统自带，支持中文和数学符号
- **最佳用途**: 本地开发测试

### 3. Source Han Sans CN
- **文件名**: `SourceHanSansCN-Regular.otf`
- **下载**: https://github.com/adobe-fonts/source-han-sans/releases
- **特点**: Adobe 出品的开源中文字体

### 4. DejaVu Sans (轻量级备选)
- **文件名**: `DejaVuSans.ttf`
- **下载**: https://dejavu-fonts.github.io/
- **特点**: 免费字体，包含数学符号，但不支持中文

## 📦 快速安装

### 方法 1：自动下载脚本

```bash
cd /Users/enithz/Desktop/pdfnew/fonts
./download_font.sh
```

如果脚本失败，请使用方法 2 手动下载。

### 方法 2：手动下载（推荐）

1. **访问下载页面**：
   - Google Fonts: https://fonts.google.com/noto/specimen/Noto+Sans+SC
   - 点击 "Download family" 按钮

2. **放置字体文件**：
   ```bash
   # 将下载的字体文件复制到 fonts 目录
   cp ~/Downloads/NotoSansSC-Regular.ttf /Users/enithz/Desktop/pdfnew/fonts/
   # 或
   cp ~/Downloads/NotoSansCJKsc-Regular.otf /Users/enithz/Desktop/pdfnew/fonts/
   ```

3. **提交到 Git**：
   ```bash
   git add fonts/NotoSans*.ttf
   git commit -m "Add Noto Sans CJK SC font for PDF generation"
   ```

## ⚙️ 配置方法

### 本地开发
无需额外配置，应用会自动使用 `Arial-Unicode.ttf` 符号链接。

### Zeabur 部署

**在 Zeabur 环境变量中设置**：
```bash
PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf
```

或者根据您下载的字体文件名：
```bash
PDF_FONT_PATH=/app/fonts/NotoSansSC-Regular.ttf
```

## 🔄 字体加载顺序

应用按以下顺序尝试加载字体：

1. **环境变量** `PDF_FONT_PATH` 指定的路径
2. **项目 fonts/ 目录**中的字体文件（NotoSans, SourceHan, DejaVu 等）
3. **系统字体**（macOS、Linux、Windows）
4. **内置字体**：ReportLab 的 CID 字体（最后回退）

## ✅ 验证安装

运行应用后，查看日志输出：

```bash
python app.py
```

成功加载字体时会显示：
```
✓ 成功注册字体: /path/to/font.otf
```

## 📝 文件清单

```
fonts/
├── README.md              # 本文件
├── FONT_SETUP.md         # 详细配置指南
├── download_font.sh      # 自动下载脚本
├── Arial-Unicode.ttf     # 系统字体符号链接（本地开发用）
└── NotoSansCJKsc-Regular.otf  # 需要手动下载（生产部署用）
```

## ⚠️ 注意事项

- 字体文件较大（10-25 MB），请确保有足够空间
- `.gitignore` 已配置允许提交字体文件
- 确保字体文件格式正确（.ttf 或 .otf）
- Zeabur 部署时字体文件会被包含在容器中

## 🆘 故障排除

详细的故障排除指南请查看 `FONT_SETUP.md` 文件。

常见问题：
- **PDF 显示黑色问号**：字体未正确加载，检查文件路径和权限
- **Zeabur 部署后乱码**：环境变量路径不匹配，确认使用 `/app/fonts/...`

