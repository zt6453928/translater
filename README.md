# PDF翻译器

基于Flask的PDF文档翻译工具，支持多种翻译模式和AI公式修正。

## 功能特点

- 📄 PDF文件上传和智能解析
- 🔄 混合翻译模式（DeepLX快速翻译 + AI公式修正）
- 🤖 支持多种AI模型
- 🎨 现代化Web界面
- ⚙️ 灵活的API配置
- 🚀 一键部署到Zeabur

## 本地开发

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python app.py
```

访问 `http://127.0.0.1:8000` 查看应用。

### 生产运行（Gunicorn）

长文档翻译/AI 修正比较耗时，建议在生产使用 Gunicorn 并加载仓库自带配置防止 30s 超时：

```bash
gunicorn -c gunicorn.conf.py app:app
```

如果平台不自动读取配置文件，可使用环境变量：

```bash
GUNICORN_CMD_ARGS="--config gunicorn.conf.py" gunicorn app:app
```

## Zeabur部署

### 1. 连接GitHub仓库

在Zeabur中连接到您的GitHub仓库：`https://github.com/zt6453928/translater`

### 2. 配置环境变量

在Zeabur的环境变量设置中添加以下变量：

```bash
# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# API配置（可选，默认值已内置）
MINERU_API_TOKEN=your-mineru-token
DEEPLX_API_URL=your-deeplx-url
AI_TRANSLATE_API_URL=your-ai-api-url
AI_TRANSLATE_API_KEY=your-ai-api-key
AI_TRANSLATE_MODEL=your-model-name
```

### 3. 部署配置

- **构建命令**: `pip install -r requirements.txt`
- 推荐：**启动命令**: `gunicorn -c gunicorn.conf.py app:app`
  - 如果无法修改命令，可设置环境变量：`GUNICORN_CMD_ARGS=--config gunicorn.conf.py`
  - 或显式添加参数：`gunicorn app:app --timeout 600 --graceful-timeout 600 --workers 1 --threads 4 --worker-class gthread`
- **端口**: `8000`

## 使用说明

1. 上传PDF文件
2. 选择翻译模式（默认为混合模式）
3. 可选：配置自定义API（默认配置已可用）
4. 点击开始翻译
5. 等待翻译完成并自动下载结果

## API配置

应用支持两种API配置方式：

1. **默认配置**：无需用户配置，直接使用内置的API密钥
2. **自定义配置**：用户可以在界面中添加自己的API配置

## 许可证

MIT License
