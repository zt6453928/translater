# PDF 字体配置

这个目录用于存放 PDF 生成所需的字体文件，以确保中文和数学符号正确显示。

## 推荐字体

为了确保 PDF 生成时中文和数学符号正确显示，请添加以下字体文件之一：

### 1. Noto Sans CJK SC (推荐)
- 文件名: `NotoSansCJKsc-Regular.otf`
- 下载: https://fonts.google.com/noto/specimen/Noto+Sans+CJK+SC
- 特点: 完整的中文字符支持，包含数学符号

### 2. Source Han Sans
- 文件名: `SourceHanSansCN-Regular.otf`
- 下载: https://github.com/adobe-fonts/source-han-sans/releases
- 特点: Adobe 出品的开源中文字体

### 3. DejaVu Sans (备选)
- 文件名: `DejaVuSans.ttf`
- 下载: https://dejavu-fonts.github.io/
- 特点: 免费字体，包含大量数学符号

## 配置方法

### 方法1: 环境变量 (推荐)
在 Zeabur 环境变量中设置:
```
PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf
```

### 方法2: 配置文件
修改 `config.py` 中的 `PDF_FONT_PATH` 设置。

## 字体加载顺序

应用按以下顺序尝试加载字体:

1. 环境变量 `PDF_FONT_PATH` 指定的路径
2. 项目 `fonts/` 目录中的字体文件
3. 系统安装的字体
4. ReportLab 内置字体 (最后回退)

## 注意事项

- 字体文件较大，请根据需要选择
- 确保字体文件格式正确 (.ttf 或 .otf)
- Zeabur 部署时字体文件会被包含在容器中