# 快速开始指南

## 🚀 一键启动

```bash
# 1. 进入项目目录
cd /Users/enithz/Desktop/pdfnew

# 2. 给脚本添加执行权限（首次运行）
chmod +x run.sh

# 3. 运行启动脚本
./run.sh
```

## 🌐 访问应用

启动后，在浏览器中打开：
```
http://localhost:5000
```

## 📖 三步使用

1. **上传PDF** - 点击或拖拽PDF文件到页面
2. **开始翻译** - 点击"开始翻译"按钮
3. **下载结果** - 等待处理完成，自动下载翻译后的PDF

## ⚙️ 配置API（如需修改）

编辑 `app.py` 文件中的API配置：

```python
# MinerU API Token
MINERU_API_TOKEN = "你的Token"

# DeepLX API URL  
DEEPLX_API_URL = "你的API地址"
```

## 📋 系统要求

- Python 3.7 或更高版本
- 稳定的网络连接
- 支持的系统：macOS, Linux, Windows

## 🎯 就这么简单！

现在你可以开始翻译PDF文档了！

详细说明请查看：
- `README.md` - 完整项目文档
- `USAGE.md` - 详细使用指南














