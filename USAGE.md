# 使用指南

## 📦 安装步骤

### 方法一：使用启动脚本（推荐）

```bash
# 给脚本添加执行权限
chmod +x run.sh

# 运行启动脚本
./run.sh
```

启动脚本会自动：
1. 检查Python环境
2. 创建虚拟环境（如果不存在）
3. 安装所有依赖
4. 启动应用

### 方法二：手动安装

```bash
# 1. 创建虚拟环境（可选但推荐）
python3 -m venv venv

# 2. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python app.py
```

## 🌐 访问应用

启动成功后，在浏览器中访问：

```
http://localhost:5000
```

## 📖 使用步骤

### 1. 上传PDF文件

有两种方式上传文件：

**方式一：点击上传**
- 点击页面中央的"选择文件"按钮
- 在文件选择器中选择PDF文件

**方式二：拖拽上传**
- 直接将PDF文件拖拽到上传区域
- 松开鼠标即可完成上传

### 2. 开始翻译

- 文件上传后，会显示文件信息
- 点击"开始翻译"按钮
- 系统会自动进行以下步骤：
  1. 📤 上传文件到服务器
  2. 🔍 使用MinerU解析PDF内容
  3. 🌐 使用DeepLX翻译文本
  4. 📝 生成新的PDF文件

### 3. 查看进度

翻译过程中会显示进度条和状态信息：
- "正在上传文件..." 
- "正在解析PDF..."
- "正在翻译内容..."
- "生成PDF文件..."

### 4. 下载结果

- 翻译完成后，文件会自动下载
- 下载的文件名格式：`translated_原文件名.pdf`
- 可以点击"重新翻译"进行新的翻译任务

## ⚙️ 配置说明

### API配置

如需修改API配置，编辑 `app.py` 文件：

```python
# MinerU API Token
MINERU_API_TOKEN = "你的Token"

# DeepLX API URL
DEEPLX_API_URL = "你的API地址"
```

或使用环境变量：

```bash
export MINERU_API_TOKEN="你的Token"
export DEEPLX_API_URL="你的API地址"
```

### 高级配置

编辑 `config.py` 文件可以修改：

**文件上传配置**
```python
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 最大文件大小
ALLOWED_EXTENSIONS = {'pdf'}  # 允许的文件格式
```

**MinerU参数**
```python
MINERU_PARAMS = {
    "is_ocr": True,              # OCR识别
    "include_image_base64": True, # 包含图片
    "formula_enable": True,       # 公式识别
    "table_enable": True,         # 表格识别
    # ... 更多参数
}
```

**翻译参数**
```python
TRANSLATION_SOURCE_LANG = "EN"  # 源语言
TRANSLATION_TARGET_LANG = "ZH"  # 目标语言
```

## 🔍 支持的文件格式

- ✅ PDF (.pdf)
- 📄 文本型PDF
- 🖼️ 扫描型PDF（需OCR）
- 📊 包含表格的PDF
- 🔢 包含公式的PDF
- 🖼️ 包含图片的PDF

## ⚠️ 限制说明

1. **文件大小**: 单个文件最大 50MB
2. **文件格式**: 仅支持 PDF 格式
3. **语言**: 当前仅支持英文到中文的翻译
4. **处理时间**: 大文件可能需要几分钟
5. **API限制**: 受API服务商的调用限制

## 🐛 故障排除

### 问题1: 无法启动应用

**解决方案**:
```bash
# 检查Python版本
python3 --version  # 需要 3.7+

# 检查端口是否被占用
lsof -i :5000

# 更换端口（修改app.py最后一行）
app.run(debug=True, host='0.0.0.0', port=8080)
```

### 问题2: 依赖安装失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 单独安装问题依赖
pip install Flask requests requests-toolbelt reportlab markdown

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3: 上传失败

**检查项**:
- 文件是否为PDF格式
- 文件大小是否超过50MB
- 网络连接是否正常

### 问题4: 翻译失败

**可能原因**:
- API Token过期或无效
- API服务暂时不可用
- 网络连接问题
- PDF格式不支持

**解决方案**:
```bash
# 检查API Token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://ai.gitee.com/v1/task/test

# 查看详细错误日志
# 在终端中查看服务器输出
```

### 问题5: PDF格式错乱

**说明**:
- 复杂的PDF格式可能无法完美保持
- 建议使用标准格式的PDF文档

**建议**:
- 使用文本型PDF而非扫描件
- 避免过于复杂的排版
- 大文件可以分割后翻译

## 💡 使用技巧

1. **批量翻译**: 一次翻译一个文件，完成后可继续上传新文件

2. **最佳效果**: 使用文本型PDF获得最佳翻译效果

3. **网络要求**: 确保稳定的网络连接，避免中断

4. **文件命名**: 使用英文文件名避免编码问题

5. **结果检查**: 翻译完成后建议检查重要内容的准确性

## 📞 获取帮助

如遇到问题：

1. 查看终端的错误日志
2. 检查 `README.md` 中的常见问题
3. 查看本使用指南的故障排除部分
4. 在GitHub上提交Issue

## 🎯 最佳实践

- ✅ 使用清晰的PDF文档
- ✅ 确保网络连接稳定
- ✅ 合理控制文件大小
- ✅ 定期检查API配额
- ✅ 保存重要的翻译结果

---

**祝您使用愉快！** 🎉












