# PDF翻译器 - 英译中

一个功能强大的PDF翻译工具，支持将英文PDF文档翻译成中文，保持原格式并支持图片。

## ✨ 功能特点

- 🔍 **智能解析**: 使用 MinerU 2.5 API 进行高质量PDF解析
- 🌐 **准确翻译**: 集成 DeepLX API 提供专业级翻译
- 📝 **格式保持**: 保留原PDF的排版和格式
- 🖼️ **图片支持**: 支持包含图片的PDF文档
- 💻 **简洁界面**: 现代化的Web界面，操作简单直观
- ⚡ **快速处理**: 异步处理，实时显示进度

## 📋 系统要求

- Python 3.7+
- 支持的操作系统: Windows, macOS, Linux

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

在 `app.py` 中配置你的API密钥（已预配置）：

```python
# MinerU API配置
MINERU_API_TOKEN = "你的MinerU API Token"

# DeepLX API配置
DEEPLX_API_URL = "你的DeepLX API地址"
```

### 3. 启动应用

```bash
python app.py
```

### 4. 访问应用

在浏览器中打开: `http://localhost:5000`

## 📖 使用说明

1. **上传PDF文件**
   - 点击上传区域或拖拽PDF文件到页面
   - 支持最大50MB的PDF文件

2. **开始翻译**
   - 点击"开始翻译"按钮
   - 等待系统处理（包括解析、翻译、生成）

3. **下载结果**
   - 翻译完成后，文件会自动下载
   - 文件名格式: `translated_原文件名.pdf`

## 🔧 技术架构

### 后端
- **Flask**: Web框架
- **Requests**: HTTP请求库
- **ReportLab**: PDF生成库
- **Markdown**: 内容处理

### API集成
- **MinerU 2.5 API**: PDF解析和内容提取
- **DeepLX API**: 文本翻译服务

### 前端
- **HTML5/CSS3**: 现代化界面
- **JavaScript**: 交互逻辑
- **响应式设计**: 支持各种屏幕尺寸

## 📁 项目结构

```
pdfnew/
├── app.py              # Flask主应用
├── requirements.txt    # Python依赖
├── README.md          # 项目说明
├── templates/         # HTML模板
│   └── index.html    # 主页面
└── static/           # 静态资源
    ├── css/
    │   └── style.css # 样式文件
    └── js/
        └── main.js   # 前端脚本
```

## ⚙️ 配置选项

### MinerU参数
```python
{
    "is_ocr": True,              # 启用OCR识别
    "include_image_base64": True, # 包含图片Base64
    "formula_enable": True,       # 启用公式识别
    "table_enable": True,         # 启用表格识别
    "layout_model": "doclayout_yolo", # 布局模型
    "output_format": "md"         # 输出格式（Markdown）
}
```

### 翻译参数
```python
{
    "source_lang": "EN",  # 源语言（英文）
    "target_lang": "ZH"   # 目标语言（中文）
}
```

## 🔍 工作流程

1. **文件上传**: 用户上传PDF文件到服务器
2. **PDF解析**: 调用MinerU API解析PDF内容为Markdown
3. **内容翻译**: 使用DeepLX API逐段翻译文本
4. **PDF生成**: 将翻译后的内容重新生成为PDF
5. **文件下载**: 返回翻译后的PDF文件给用户

## ⚠️ 注意事项

- 翻译速度取决于PDF页数和API响应时间
- 大文件可能需要较长处理时间
- 确保网络连接稳定，以便访问API
- 复杂的PDF格式可能影响最终效果
- API调用次数可能有限制，请查看服务商说明

## 🐛 常见问题

### 1. 上传失败
- 检查文件大小是否超过50MB
- 确认文件格式为PDF

### 2. 翻译超时
- 检查网络连接
- 尝试分割大文件后再翻译

### 3. 格式错乱
- 部分复杂PDF格式可能无法完美保持
- 建议使用标准格式的PDF文档

### 4. API错误
- 检查API Token是否有效
- 确认API服务可用性

## 📝 开发计划

- [ ] 支持更多语言对翻译
- [ ] 批量文件处理
- [ ] 自定义翻译引擎选择
- [ ] 翻译历史记录
- [ ] PDF编辑和标注功能
- [ ] 云端存储集成

## 📄 许可证

MIT License

## 👨‍💻 作者

PDF翻译器项目

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**享受翻译！** 🎉

