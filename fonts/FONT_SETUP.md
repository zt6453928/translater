# 字体配置说明

## 当前配置

项目已配置使用系统内置的 **Arial Unicode** 字体作为临时方案。

### 本地开发

`fonts/Arial-Unicode.ttf` 是指向系统字体的符号链接：
```
/System/Library/Fonts/Supplemental/Arial Unicode.ttf
```

这个字体支持：
- ✓ 中文字符
- ✓ 基本数学符号
- ✓ 希腊字母

### Zeabur 部署配置

对于 Zeabur 部署，您需要手动下载并上传字体文件。

---

## 方案 1：手动下载 Noto Sans CJK SC（推荐）

### 步骤 1：下载字体

访问以下任一网址下载：

**选项 A：Google Fonts（推荐）**
1. 访问：https://fonts.google.com/noto/specimen/Noto+Sans+SC
2. 点击右上角 "Download family" 按钮
3. 解压下载的 ZIP 文件
4. 找到 `NotoSansSC-Regular.ttf` 文件

**选项 B：GitHub Releases**
1. 访问：https://github.com/googlefonts/noto-cjk/releases
2. 下载最新的 `Sans` 包（例如：`Sans.zip`）
3. 解压并找到 `SimplifiedChinese/NotoSansCJKsc-Regular.otf`

**选项 C：直接链接（如果网络允许）**
```bash
cd /Users/enithz/Desktop/pdfnew/fonts
curl -L -o NotoSansCJKsc-Regular.otf \
  "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
```

### 步骤 2：放置字体文件

将下载的字体文件复制到：
```
/Users/enithz/Desktop/pdfnew/fonts/NotoSansCJKsc-Regular.otf
```

或使用命令：
```bash
cp ~/Downloads/NotoSansCJKsc-Regular.otf /Users/enithz/Desktop/pdfnew/fonts/
```

### 步骤 3：配置环境变量

在 Zeabur 的环境变量中设置：
```
PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf
```

---

## 方案 2：使用当前的 Arial Unicode（临时方案）

如果暂时无法下载 Noto Sans CJK SC，可以使用当前配置：

### 本地测试

字体已自动配置，无需额外设置。

### Zeabur 部署

在 Zeabur 环境变量中设置：
```
PDF_FONT_PATH=/app/fonts/Arial-Unicode.ttf
```

然后在 Dockerfile 或构建脚本中安装 Arial Unicode 字体：
```dockerfile
RUN apt-get update && apt-get install -y \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*
```

---

## 方案 3：使用开源替代字体

### DejaVu Sans（轻量级）

适合对字体大小有要求的场景：

```bash
# 下载 DejaVu Sans
cd /Users/enithz/Desktop/pdfnew/fonts
curl -L -o DejaVuSans.ttf \
  "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
```

Zeabur 环境变量：
```
PDF_FONT_PATH=/app/fonts/DejaVuSans.ttf
```

---

## 验证字体安装

安装字体后，运行应用并检查日志：

```bash
python app.py
```

查看日志输出：
```
✓ 成功注册字体: /path/to/font.otf
```

如果看到此消息，说明字体加载成功！

---

## 字体文件大小参考

| 字体 | 文件大小 | 中文支持 | 数学符号 |
|------|---------|---------|---------|
| Noto Sans CJK SC | ~16 MB | 完整 | 完整 |
| Arial Unicode | ~24 MB | 完整 | 完整 |
| DejaVu Sans | ~757 KB | 无 | 完整 |

---

## 故障排除

### 问题：PDF 中仍显示黑色问号

**原因：** 字体文件未正确加载

**解决：**
1. 检查字体文件路径是否正确
2. 检查文件权限（应可读）
3. 查看应用日志确认字体加载状态

### 问题：Zeabur 部署后字体无效

**原因：** 容器中字体文件路径不匹配

**解决：**
1. 确认字体文件已包含在项目中（未被 .gitignore 忽略）
2. 确认环境变量 `PDF_FONT_PATH` 路径正确（通常是 `/app/fonts/...`）
3. 检查 Zeabur 构建日志

---

## 推荐配置（生产环境）

```bash
# 1. 下载 Noto Sans CJK SC 到 fonts 目录
# 2. 提交到 Git
git add fonts/NotoSansCJKsc-Regular.otf
git commit -m "Add Noto Sans CJK SC font for PDF generation"

# 3. 在 Zeabur 设置环境变量
PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf

# 4. 部署
git push
```

完成！PDF 应该能够正确显示所有中文和数学符号了。
