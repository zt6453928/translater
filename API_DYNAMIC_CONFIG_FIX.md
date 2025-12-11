# API动态配置修复说明

## 修复日期
2025年12月11日

## 问题描述

1. **解析API未使用前端配置**：尽管前端可以配置自定义的解析API Key，但后端仍然使用硬编码的API配置，导致用户配置的新API没有生效。

2. **翻译API未使用前端配置**：虽然翻译API函数已经使用了Config类，但没有接收前端传来的动态配置，用户添加的新翻译API无法被使用。

3. **翻译API URL输入不便**：用户需要输入完整的API endpoint（如 `https://b4u.qzz.io/v1/chat/completions`），而不能只输入基础URL。

## 修复内容

### 1. 解析API动态配置 ✅

**修改文件**: `app.py`

#### 修改的函数:

**`parse_pdf_with_mineru(filepath, options=None, api_token=None)`**
- 新增 `api_token` 参数，支持传入自定义API Token
- 如果传入了 `api_token`，优先使用；否则使用配置文件中的默认值
- 动态构建请求headers，不再使用全局的 `mineru_headers`

```python
# 修改前
def parse_pdf_with_mineru(filepath, options=None):
    # 使用硬编码的 MINERU_API_TOKEN 和 mineru_headers

# 修改后
def parse_pdf_with_mineru(filepath, options=None, api_token=None):
    from config import Config
    token = api_token or Config.MINERU_API_TOKEN
    # 动态构建 headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": encoder.content_type
    }
```

**`poll_mineru_task(task_id, api_token=None)`**
- 新增 `api_token` 参数
- 动态构建请求headers

```python
# 修改前
def poll_mineru_task(task_id):
    response = requests.get(status_url, headers=mineru_headers, timeout=10)

# 修改后
def poll_mineru_task(task_id, api_token=None):
    from config import Config
    token = api_token or Config.MINERU_API_TOKEN
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(status_url, headers=headers, timeout=10)
```

### 2. 翻译API动态配置 ✅

**修改文件**: `app.py`

#### 修改的函数:

**`translate_with_ai(text, ..., api_url=None, api_key=None, model=None)`**
- 新增三个参数：`api_url`, `api_key`, `model`
- 支持动态配置翻译API
- **智能URL处理**：如果用户只输入基础URL（如 `https://b4u.qzz.io/`），自动补全为 `https://b4u.qzz.io/v1/chat/completions`

```python
# 修改后的逻辑
translate_api_url = api_url or Config.AI_TRANSLATE_API_URL

# 智能补全URL
if translate_api_url and not translate_api_url.endswith('/chat/completions'):
    translate_api_url = translate_api_url.rstrip('/')
    if not translate_api_url.endswith('/v1'):
        translate_api_url += '/v1'
    translate_api_url += '/chat/completions'
    print(f"✓ 自动补全翻译API URL: {translate_api_url}")
```

**`translate_markdown_content_with_ai(markdown_text, api_url=None, api_key=None, model=None)`**
- 新增三个参数，传递给 `translate_with_ai` 函数
- 支持分块翻译时使用自定义API配置

### 3. 主路由接收并传递API配置 ✅

**修改文件**: `app.py`

在 `/translate` 路由中：

```python
# 获取前端传来的API配置
parse_api_token = request.form.get('parse_api_token')
translate_api_url = request.form.get('translate_api_url')
translate_api_key = request.form.get('translate_api_key')
translate_api_model = request.form.get('translate_api_model')

# 打印配置信息（便于调试）
print("\n" + "=" * 50)
print("API配置信息:")
if parse_api_token:
    print(f"✓ 使用自定义解析API Token: {parse_api_token[:10]}...")
# ... 更多日志

# 调用解析函数时传入配置
result = parse_pdf_with_mineru(upload_path, mineru_options, api_token=parse_api_token)
task_result = poll_mineru_task(task_id, api_token=parse_api_token)

# 调用翻译函数时传入配置
translated_content = translate_markdown_content_with_ai(
    markdown_content,
    api_url=translate_api_url,
    api_key=translate_api_key,
    model=translate_api_model
)
```

### 4. 清理硬编码配置 ✅

**修改文件**: `app.py`

删除了以下全局硬编码变量：
```python
# 已删除
MINERU_API_URL = "https://ai.gitee.com/v1/async/documents/parse"
MINERU_API_TOKEN = "V5PWW7GYB8NOTZGQ6EEF4IJL3TIGXJF3YU2L371P"
DEEPLX_API_URL = "https://api.deeplx.org/..."
mineru_headers = {...}
```

所有API配置现在统一使用 `config.py` 中的 `Config` 类，并支持动态传入。

### 5. 更新前端提示 ✅

**修改文件**: `static/js/main.js`

更新了翻译API URL的输入提示：
```javascript
// 修改前
placeholder="https://api.example.com/v1/chat/completions"

// 修改后
placeholder="https://b4u.qzz.io/"
```

提示用户只需输入基础URL，后端会自动补全endpoint。

## 使用说明

### 1. 解析API配置

在前端界面的"参数配置" → "API配置" → "解析API Key"中：
1. 点击"添加"按钮
2. 输入API Key（例如：`V5PWW7GYB8NOTZGQ6EEF4IJL3TIGXJF3YU2L371P`）
3. 选中该API配置（单选按钮）
4. 开始翻译时会使用该API

**如果不添加配置**：使用 `config.py` 中的默认配置

### 2. 翻译API配置

在前端界面的"参数配置" → "API配置" → "翻译AI API"中：
1. 点击"添加"按钮
2. **API URL**：只需输入基础URL，例如：
   - ✅ `https://b4u.qzz.io/`
   - ✅ `https://b4u.qzz.io`
   - ✅ `https://api.openai.com/`
   - 后端会自动补全为：`https://b4u.qzz.io/v1/chat/completions`
3. **API Key**：输入你的API密钥
4. **模型名称**：输入模型名称（如：`claude-4.5-sonnet-think`）
5. 选中该API配置
6. 开始翻译时会使用该API

**如果不添加配置**：使用 `config.py` 中的默认配置

## URL自动补全规则

翻译API URL的自动补全逻辑：

```
输入: https://b4u.qzz.io
输出: https://b4u.qzz.io/v1/chat/completions

输入: https://b4u.qzz.io/
输出: https://b4u.qzz.io/v1/chat/completions

输入: https://b4u.qzz.io/v1
输出: https://b4u.qzz.io/v1/chat/completions

输入: https://api.openai.com/v1/chat/completions
输出: https://api.openai.com/v1/chat/completions （已完整，不修改）
```

## 配置优先级

```
前端用户配置 > config.py配置文件 > 代码默认值
```

1. **优先使用**：用户在前端界面配置并选中的API
2. **其次使用**：`config.py` 中的配置（可通过环境变量覆盖）
3. **最后使用**：代码中的默认值（如果存在）

## 调试信息

修复后，在运行时会输出详细的配置信息：

```
==================================================
API配置信息:
✓ 使用自定义解析API Token: V5PWW7GYB8...
✓ 使用自定义翻译API URL: https://b4u.qzz.io/
✓ 使用自定义翻译API Key: sk-xMADfH...
✓ 使用自定义翻译模型: claude-4.5-sonnet-think
==================================================

✓ 自动补全翻译API URL: https://b4u.qzz.io/v1/chat/completions
正在使用AI翻译（长度: 1234 字符）...
使用模型: claude-4.5-sonnet-think
```

## 测试建议

1. **测试解析API切换**：
   - 添加多个解析API Key
   - 切换不同的API，验证是否使用了正确的Key

2. **测试翻译API切换**：
   - 添加多个翻译API配置
   - 切换不同的API，验证是否调用了正确的endpoint

3. **测试URL自动补全**：
   - 输入不同格式的URL，验证是否正确补全

4. **测试默认配置**：
   - 不添加任何自定义配置，验证是否使用默认配置

## 兼容性说明

- ✅ 向后兼容：如果用户不配置自定义API，系统会使用默认配置
- ✅ 灵活切换：用户可以随时添加、删除、切换API配置
- ✅ 配置持久化：API配置保存在浏览器 localStorage，刷新页面后依然保留

## 相关文件

- `app.py` - 主要修改文件，包含所有API调用逻辑
- `config.py` - 默认配置文件
- `static/js/main.js` - 前端API管理逻辑
- `templates/index.html` - 前端界面
