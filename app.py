import requests
from requests_toolbelt import MultipartEncoder
import os
import time
import json
import contextlib
import mimetypes
from flask import Flask, render_template, request, send_file, jsonify
import tempfile
import shutil
import re
import base64
from io import BytesIO
from config import Config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 创建安全的上传目录 (使用 /tmp 目录，因为 /app 在容器中是只读的)
import os
UPLOAD_DIR = '/tmp/uploads'
DEBUG_DIR = '/tmp/debug_logs'

# 确保目录存在并设置权限
for directory in [UPLOAD_DIR, DEBUG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        # 设置目录权限为755 (rwxr-xr-x)
        os.chmod(directory, 0o755)

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# 禁用Flask的默认安全头
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False

# 添加CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def parse_pdf_with_mineru(filepath, options=None, api_token=None):
    """使用MinerU API解析PDF"""
    from config import Config
    
    # 使用传入的token或配置文件中的token
    token = api_token or Config.MINERU_API_TOKEN
    api_url = Config.MINERU_API_URL
    
    base_payload = {
        "model": "MinerU2.5",
        "is_ocr": True,
        "include_image_base64": True,
        "formula_enable": True,
        "table_enable": True,
        "layout_model": "doclayout_yolo",
        "output_format": "md"
    }

    payload = base_payload.copy()
    if options:
        for key, value in options.items():
            if value is not None:
                payload[key] = value
    
    # 调试：打印 payload
    print("\n" + "=" * 50)
    print("构建的 payload:")
    for k, v in payload.items():
        print(f"  {k}: {v} (type: {type(v).__name__})")
    print("=" * 50 + "\n")

    fields = []
    for key in [
        "model",
        "is_ocr",
        "include_image_base64",
        "formula_enable",
        "table_enable",
        "layout_model",
        "output_format",
        "end_pages",
        "language"
    ]:
        if key not in payload:
            continue
        value = payload[key]
        if isinstance(value, bool):
            value = str(value).lower()
        elif value is None:
            continue
        # 跳过空字符串（特别是 end_pages 等可选参数）
        elif isinstance(value, str) and not value.strip():
            continue
        fields.append((key, str(value)))

    # 打印实际发送的字段（用于调试）
    print("=" * 50)
    print("发送到 MinerU API 的参数:")
    for key, value in fields:
        print(f"  {key}: {value}")
    print(f"使用API Token: {token[:10]}..." if token else "未配置Token")
    print("=" * 50)
    
    with contextlib.ExitStack() as stack:
        name = os.path.basename(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        fields.append(("file", (name, stack.enter_context(open(filepath, "rb")),
                                mime_type or "application/octet-stream")))
        encoder = MultipartEncoder(fields)
        
        # 使用动态的headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": encoder.content_type
        }
        
        response = requests.post(api_url, headers=headers, data=encoder)
        return response.json()


def poll_mineru_task(task_id, api_token=None):
    """轮询MinerU任务状态"""
    from config import Config

    # 使用传入的token或配置文件中的token
    token = api_token or Config.MINERU_API_TOKEN

    # 动态构建状态查询URL（基于API的base URL）
    status_url = f"https://ai.gitee.com/v1/task/{task_id}"

    # 减少总超时时间到10分钟，更适合云环境
    timeout = 10 * 60  # 10分钟
    retry_interval = 3  # 3秒检查一次，减少阻塞时间
    attempts = 0
    max_attempts = int(timeout / retry_interval)

    # 构建headers
    headers = {
        "Authorization": f"Bearer {token}"
    }

    print(f"开始轮询任务状态，总超时: {timeout//60}分钟...")

    while attempts < max_attempts:
        attempts += 1

        # 每30次检查（90秒）显示一次进度
        if attempts % 30 == 1:
            elapsed = (attempts - 1) * retry_interval
            print(f"  📊 已等待 {elapsed//60}分{elapsed%60}秒，正在处理PDF...")

        try:
            response = requests.get(status_url, headers=headers, timeout=10)
            result = response.json()

            if result.get("error"):
                print(f"  ❌ API错误: {result['error']}: {result.get('message', '未知错误')}")
                raise ValueError(f"{result['error']}: {result.get('message', '未知错误')}")

            status = result.get("status", "unknown")

            if status == "success":
                print("  ✅ 任务完成！")
                # 保存完整结果到文件用于调试
                debug_dir = '/tmp/debug_logs'
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir, exist_ok=True)
                debug_file = os.path.join(debug_dir, f"mineru_result_{task_id}.json")
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"  📄 调试文件已保存: {debug_file}")
                except Exception as e:
                    print(f"  ⚠️ 无法保存调试文件: {e}")
                return result
            elif status in ["failed", "cancelled"]:
                print(f"  ❌ 任务{status}")
                raise ValueError(f"任务{status}")
            else:
                # 短暂休眠，避免过度占用资源
                time.sleep(retry_interval)
                continue

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ 网络请求失败，重试中: {e}")
            time.sleep(retry_interval)
            continue

    print(f"  ⏰ 任务超时 (已等待 {timeout//60}分钟)")
    raise TimeoutError(f"任务处理超时，已等待 {timeout//60} 分钟")


def translate_with_ai(text, source_lang="EN", target_lang="ZH", api_url=None, api_key=None, model=None, max_retries=None):
    """使用AI API翻译文本并处理数学公式，支持自动重试"""
    from config import Config
    import time
    
    if not text or not text.strip():
        return text
    
    # 使用传入的配置或默认配置
    translate_api_url = api_url or Config.AI_TRANSLATE_API_URL
    translate_api_key = api_key or Config.AI_TRANSLATE_API_KEY
    translate_model = model or Config.AI_TRANSLATE_MODEL
    max_retries = max_retries or Config.AI_TRANSLATE_MAX_RETRIES
    
    # 处理API URL：如果用户只输入了基础URL，自动添加endpoint
    if translate_api_url and not translate_api_url.endswith('/chat/completions'):
        # 移除末尾的斜杠
        translate_api_url = translate_api_url.rstrip('/')
        # 检查是否已经有 /v1 后缀
        if not translate_api_url.endswith('/v1'):
            translate_api_url += '/v1'
        # 添加 /chat/completions
        translate_api_url += '/chat/completions'
        print(f"✓ 自动补全翻译API URL: {translate_api_url}", flush=True)
    
    # 构建系统提示
    system_prompt = """你是一个专业的学术论文翻译专家。请将英文学术内容翻译成中文，并严格遵循以下规则：

## 核心要求
1. **完整翻译**：必须翻译所有英文内容，不要遗漏任何段落、句子或短语
2. **翻译质量**：使用准确、流畅的学术中文，保持专业性
3. **完全清除方框字符**：文本中任何显示为方框(□)的字符都必须被移除或替换为正确的字符
4. **正确处理参考文献标注**：上标数字之间不要有空格或其他字符

## 数学公式处理（关键！）
将所有LaTeX数学公式转换为Unicode格式，具体规则：

### 上标（Superscripts）
- 数字：⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹
- 符号：⁺ ⁻ ⁼ ⁽ ⁾
- 示例：$^{13}C$ → ¹³C，$^{12-14}$ → ¹²⁻¹⁴，$^{2,18}$ → ²,¹⁸

### 下标（Subscripts）
- 数字：₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
- 符号：₊ ₋ ₌ ₍ ₎
- 示例：$O_2$ → O₂，$H_2O$ → H₂O

### 希腊字母
α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω

### 数学符号
± ∓ × · ÷ ≤ ≥ ≠ ≈ ≡ ∞ ∑ ∏ ∫ ∂ ∇ √ ∼ ≪ ≫

## 特殊处理
1. **作者上标**：如 "Wang $^{1,2,3}$" → "Wang ¹,²,³"（注意：数字之间只用逗号，不要有空格或其他字符）
2. **波浪号**：$\\sim$ 或 ~ → ∼（使用Unicode波浪号 U+223C）
3. **范围标注**：如 $^{13-15}$ → ¹³⁻¹⁵（使用Unicode上标减号）
4. **百分号**：‰（千分号）保持不变

## 格式保持
- 保留所有Markdown标记：# ## ### * ** [] () 等
- 保持段落和换行结构
- 图片标记保持原样

## 不要翻译
- 人名、地名
- 期刊名、机构名
- 图片的base64数据
- 已经是中文的内容

## 输出要求
**必须完整翻译所有内容！** 确保输出包含输入中的每一个段落、每一句话。

只返回翻译后的纯文本内容，不要添加任何说明、解释或元信息。

**严格禁止：**
- ❌ 不要使用HTML标签（如 <sup>、<sub>、<b>、<i> 等）
- ❌ 不要有方框字符(□)
- ❌ 不要有任何其他标记语言
- ❌ 不要遗漏任何段落或句子

**必须使用：**
- ✅ Unicode上标字符：⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻
- ✅ Unicode下标字符：₀₁₂₃₄₅₆₇₈₉₊₋
- ✅ 纯文本格式
- ✅ 翻译所有英文内容

**检查清单：**
- [ ] 所有段落都已翻译
- [ ] 没有英文句子残留
- [ ] 保持了原文的完整结构"""

    # 构建请求
    headers = {
        "Authorization": f"Bearer {translate_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": translate_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "max_tokens": Config.AI_TRANSLATE_MAX_TOKENS,
        "temperature": 0.3  # 较低的temperature以保持一致性
    }
    
    # 重试逻辑
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # 重试前等待，使用指数退避策略
                wait_time = min(2 ** attempt, 10)  # 最多等待10秒
                print(f"⏳ 等待 {wait_time} 秒后重试（第 {attempt + 1}/{max_retries} 次）...", flush=True)
                time.sleep(wait_time)
            
            print(f"正在使用AI翻译（长度: {len(text)} 字符）{'[重试 ' + str(attempt + 1) + ']' if attempt > 0 else ''}...", flush=True)
            if attempt == 0:  # 只在第一次尝试时打印模型信息
                print(f"使用模型: {translate_model}", flush=True)
            
            response = requests.post(
                translate_api_url,
                headers=headers,
                json=payload,
                timeout=Config.AI_TRANSLATE_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取翻译结果
            if "choices" in result and len(result["choices"]) > 0:
                translated_text = result["choices"][0]["message"]["content"]
                
                # 如果使用 think 模型，过滤掉思考过程标签
                if "<think>" in translated_text and "</think>" in translated_text:
                    # 移除 <think>...</think> 标签及其内容
                    import re
                    translated_text = re.sub(r'<think>.*?</think>\s*', '', translated_text, flags=re.DOTALL)
                    print(f"✓ AI翻译完成（已过滤思考过程，输出长度: {len(translated_text)} 字符）", flush=True)
                else:
                    print(f"✓ AI翻译完成（输出长度: {len(translated_text)} 字符）", flush=True)
                
                # 清理HTML标签并转换为Unicode
                translated_text = clean_html_tags(translated_text)
                if '<sup>' in result["choices"][0]["message"]["content"] or '<sub>' in result["choices"][0]["message"]["content"]:
                    print(f"✓ 已清理HTML标签并转换为Unicode字符", flush=True)
                
                # 检查翻译完整性
                is_complete, remaining_words, original_words = check_translation_completeness(text, translated_text)
                if not is_complete:
                    print(f"⚠️ 警告：翻译可能不完整！", flush=True)
                    print(f"   原文英文单词: {original_words}, 译文残留英文单词: {remaining_words}", flush=True)
                    print(f"   建议：增加 AI_TRANSLATE_MAX_TOKENS 或分块处理", flush=True)
                else:
                    print(f"✓ 翻译完整性检查通过（残留英文单词: {remaining_words}/{original_words}）", flush=True)
                
                return translated_text.strip()
            else:
                print(f"⚠️ AI翻译响应格式异常: {result}", flush=True)
                # 响应格式异常时也重试
                if attempt < max_retries - 1:
                    continue
                return text
                
        except requests.exceptions.Timeout:
            print(f"⚠️ AI翻译超时", flush=True)
            if attempt < max_retries - 1:
                continue
            print(f"⚠️ 达到最大重试次数，保留原文", flush=True)
            return text
        except requests.exceptions.ProxyError as e:
            print(f"⚠️ 代理连接错误: {e}", flush=True)
            if attempt < max_retries - 1:
                continue
            print(f"⚠️ 达到最大重试次数，保留原文", flush=True)
            return text
        except requests.exceptions.ConnectionError as e:
            print(f"⚠️ 网络连接错误: {e}", flush=True)
            if attempt < max_retries - 1:
                continue
            print(f"⚠️ 达到最大重试次数，保留原文", flush=True)
            return text
        except Exception as e:
            print(f"⚠️ AI翻译错误: {e}", flush=True)
            if attempt < max_retries - 1:
                continue
            print(f"⚠️ 达到最大重试次数，保留原文", flush=True)
            return text
    
    # 如果所有重试都失败，返回原文
    return text


def translate_with_deeplx(text, source_lang="EN", target_lang="ZH", max_retries=None):
    """使用DeepLX API快速翻译文本（支持重试）"""
    from config import Config
    import time
    
    if not text or not text.strip():
        return text
    
    max_retries = max_retries or Config.DEEPLX_MAX_RETRIES
    
    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = min(2 ** attempt, 5)
                print(f"⏳ DeepLX重试等待 {wait_time} 秒（第 {attempt + 1}/{max_retries} 次）...", flush=True)
                time.sleep(wait_time)
            
            response = requests.post(Config.DEEPLX_API_URL, json=payload, timeout=Config.DEEPLX_TIMEOUT)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 200:
                translated = result.get("data", text)
                return translated
            else:
                print(f"⚠️ DeepLX翻译失败: {result}", flush=True)
                if attempt < max_retries - 1:
                    continue
                return text
                
        except requests.exceptions.Timeout:
            print(f"⚠️ DeepLX请求超时", flush=True)
            if attempt < max_retries - 1:
                continue
            return text
        except Exception as e:
            print(f"⚠️ DeepLX翻译错误: {e}", flush=True)
            if attempt < max_retries - 1:
                continue
            return text
    
    return text


def translate_markdown_content_with_ai(markdown_text, api_url=None, api_key=None, model=None):
    """使用AI翻译Markdown内容，智能处理格式和数学公式"""
    # 先清理整个文本的Unicode字符
    markdown_text = clean_unicode_characters(markdown_text, debug=False)
    
    # 优化分块大小，减少单次请求的负担
    from config import Config
    max_chunk_size = Config.AI_TRANSLATE_CHUNK_SIZE  # 使用配置文件中的分块大小
    
    if len(markdown_text) <= max_chunk_size:
        # 如果内容不长，一次性翻译
        print(f"内容适中（{len(markdown_text)}字符），一次性翻译...", flush=True)
        translated_text = translate_with_ai(markdown_text, api_url=api_url, api_key=api_key, model=model)
        
        # 验证翻译是否完整
        if len(translated_text) < len(markdown_text) * 0.5:
            print(f"⚠️ 警告：翻译输出较短（{len(translated_text)}字符），可能不完整", flush=True)
        
        return translated_text
    else:
        # 如果内容较长，按段落分块翻译
        print(f"内容较长（{len(markdown_text)}字符），分块翻译...", flush=True)
        print(f"📊 使用分块大小: {max_chunk_size} 字符", flush=True)
        
        # 按双换行符分割段落
        paragraphs = markdown_text.split('\n\n')
        translated_paragraphs = []
        
        current_chunk = ""
        chunk_count = 0
        total_chunks_estimate = len(markdown_text) // max_chunk_size + 1
        
        for i, para in enumerate(paragraphs):
            # 如果单个段落就超过限制，需要进一步分割
            if len(para) > max_chunk_size:
                # 先翻译当前累积的块
                if current_chunk:
                    chunk_count += 1
                    print(f"📝 翻译块 {chunk_count}/{total_chunks_estimate} (长度: {len(current_chunk)} 字符)...", flush=True)
                    translated_chunk = translate_with_ai(current_chunk, api_url=api_url, api_key=api_key, model=model)
                    translated_paragraphs.append(translated_chunk)
                    current_chunk = ""
                    time.sleep(0.5)  # 减少延迟
                
                # 对超大段落按句子分割
                print(f"⚠️ 发现超大段落（{len(para)} 字符），进行二次分割...", flush=True)
                sentences = para.split('. ')
                temp_chunk = ""
                
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) + 2 <= max_chunk_size:
                        temp_chunk += sentence + '. ' if not sentence.endswith('.') else sentence + ' '
                    else:
                        if temp_chunk:
                            chunk_count += 1
                            print(f"📝 翻译块 {chunk_count}/{total_chunks_estimate} (长度: {len(temp_chunk)} 字符)...", flush=True)
                            translated_chunk = translate_with_ai(temp_chunk.strip(), api_url=api_url, api_key=api_key, model=model)
                            translated_paragraphs.append(translated_chunk)
                            time.sleep(0.5)
                        temp_chunk = sentence + '. ' if not sentence.endswith('.') else sentence + ' '
                
                # 翻译剩余的句子
                if temp_chunk.strip():
                    chunk_count += 1
                    print(f"📝 翻译块 {chunk_count}/{total_chunks_estimate} (长度: {len(temp_chunk)} 字符)...", flush=True)
                    translated_chunk = translate_with_ai(temp_chunk.strip(), api_url=api_url, api_key=api_key, model=model)
                    translated_paragraphs.append(translated_chunk)
                    time.sleep(0.5)
                
                continue
            
            # 如果当前块加上这个段落不超过限制，就累积
            if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # 翻译当前块
                if current_chunk:
                    chunk_count += 1
                    print(f"📝 翻译块 {chunk_count}/{total_chunks_estimate} (长度: {len(current_chunk)} 字符)...", flush=True)
                    translated_chunk = translate_with_ai(current_chunk, api_url=api_url, api_key=api_key, model=model)
                    translated_paragraphs.append(translated_chunk)
                    time.sleep(0.5)  # 减少延迟
                
                # 开始新块
                current_chunk = para
        
        # 翻译最后一块
        if current_chunk:
            chunk_count += 1
            print(f"📝 翻译块 {chunk_count}/{total_chunks_estimate} (长度: {len(current_chunk)} 字符)...", flush=True)
            translated_chunk = translate_with_ai(current_chunk, api_url=api_url, api_key=api_key, model=model)
            translated_paragraphs.append(translated_chunk)
        
        # 合并所有翻译结果
        result = "\n\n".join(translated_paragraphs)
        print(f"✅ 完成分块翻译，共 {chunk_count} 块", flush=True)
        return result


def fix_formulas_with_ai(text, api_url=None, api_key=None, model=None):
    """使用AI API专门修正翻译后文本中的数学公式"""
    from config import Config
    import time
    import re
    
    if not text or not text.strip():
        return text
    
    # 第一步：保护图片标记，避免被AI处理
    image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    images = []
    
    def save_image(match):
        placeholder = f"<<<IMAGE_PLACEHOLDER_{len(images)}>>>"
        images.append(match.group(0))
        return placeholder
    
    # 替换图片为占位符
    text_without_images = re.sub(image_pattern, save_image, text)
    
    # 检查是否有实际的公式需要修正（如果没有，直接返回）
    has_formulas = bool(re.search(r'[\$\\]', text_without_images))
    if not has_formulas and not re.search(r'<su[bp]>', text_without_images):
        print(f"✓ 未检测到需要修正的公式，跳过AI修正", flush=True)
        return text  # 直接返回原文，保留图片
    
    # 使用传入的配置或默认配置
    translate_api_url = api_url or Config.AI_TRANSLATE_API_URL
    translate_api_key = api_key or Config.AI_TRANSLATE_API_KEY
    translate_model = model or Config.AI_TRANSLATE_MODEL
    max_retries = Config.AI_TRANSLATE_MAX_RETRIES
    
    # 处理API URL
    if translate_api_url and not translate_api_url.endswith('/chat/completions'):
        translate_api_url = translate_api_url.rstrip('/')
        if not translate_api_url.endswith('/v1'):
            translate_api_url += '/v1'
        translate_api_url += '/chat/completions'
    
    # 极度简化和严格的系统提示
    system_prompt = """你是公式修正专家。你收到的是已经翻译好的中文文本，里面可能有显示异常的数学公式。

**你的唯一任务**：修正公式显示，其他内容一字不改。

**修正规则**：
1. LaTeX公式转Unicode：$^{13}C$ → ¹³C，$O_2$ → O₂
2. 移除HTML标签：<sup>13</sup> → ¹³
3. 移除方框字符 □
4. 数学符号：$\\sim$ → ∼，$\\pm$ → ±

**严格禁止**：
❌ 不要添加任何解释或说明
❌ 不要询问用户任何问题
❌ 不要生成新内容
❌ 不要改变翻译
❌ 如果文本中有图片占位符（<<<IMAGE_PLACEHOLDER_X>>>），必须原样保留

**输出要求**：
只返回修正后的文本，保持所有内容、段落、格式完全一致。"""

    headers = {
        "Authorization": f"Bearer {translate_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": translate_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请修正以下文本中的数学公式：\n\n{text_without_images}"}
        ],
        "max_tokens": Config.AI_TRANSLATE_MAX_TOKENS,
        "temperature": 0.0  # 零temperature，保持完全一致性
    }
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = min(2 ** attempt, 10)
                print(f"⏳ 公式修正重试等待 {wait_time} 秒（第 {attempt + 1}/{max_retries} 次）...", flush=True)
                time.sleep(wait_time)
            
            print(f"🔧 正在修正数学公式（长度: {len(text_without_images)} 字符）{'[重试 ' + str(attempt + 1) + ']' if attempt > 0 else ''}...", flush=True)
            
            response = requests.post(
                translate_api_url,
                headers=headers,
                json=payload,
                timeout=Config.AI_TRANSLATE_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                fixed_text = result["choices"][0]["message"]["content"]
                
                # 过滤思考标签
                if "<think>" in fixed_text and "</think>" in fixed_text:
                    fixed_text = re.sub(r'<think>.*?</think>\s*', '', fixed_text, flags=re.DOTALL)
                
                # 清理HTML标签
                fixed_text = clean_html_tags(fixed_text)
                
                # 验证输出长度，避免AI生成无关内容
                original_len = len(text_without_images)
                output_len = len(fixed_text)
                
                # 如果输出长度差异超过50%，可能是AI生成了无关内容
                if abs(output_len - original_len) > original_len * 0.5:
                    print(f"⚠️ 警告：AI输出长度异常（原文:{original_len}, 输出:{output_len}），使用原文", flush=True)
                    fixed_text = text_without_images
                
                # 检查AI是否返回了提问或解释
                if any(phrase in fixed_text[:200] for phrase in ['I need', 'I can see', 'Could you', 'Please provide', '我需要', '请提供']):
                    print(f"⚠️ 警告：AI返回了提问而非修正结果，使用原文", flush=True)
                    fixed_text = text_without_images
                
                # 恢复图片占位符为原始图片
                for i, img in enumerate(images):
                    placeholder = f"<<<IMAGE_PLACEHOLDER_{i}>>>"
                    fixed_text = fixed_text.replace(placeholder, img)
                
                print(f"✓ 公式修正完成（输出长度: {len(fixed_text)} 字符）", flush=True)
                print(f"✓ 已恢复 {len(images)} 张图片", flush=True)
                
                return fixed_text.strip()
            else:
                print(f"⚠️ 公式修正响应格式异常", flush=True)
                if attempt < max_retries - 1:
                    continue
                return text
                
        except Exception as e:
            print(f"⚠️ 公式修正错误: {e}", flush=True)
            if attempt < max_retries - 1:
                continue
            return text
    
    # 如果所有重试都失败，返回原文（包含图片）
    return text


def translate_markdown_hybrid(markdown_text, api_url=None, api_key=None, model=None):
    """
    混合翻译模式（三步走策略）：
    1. 使用MinerU提取内容（已完成）
    2. 使用DeepLX快速翻译
    3. 使用AI修正数学公式
    """
    from config import Config
    import time
    
    print("\n" + "=" * 60)
    print("🚀 使用混合翻译模式（DeepLX + AI公式修正）")
    print("=" * 60)
    
    # 第一步：清理Unicode字符
    print("\n📋 步骤 1/3: 清理文本...")
    markdown_text = clean_unicode_characters(markdown_text, debug=False)
    print(f"✓ 文本清理完成（长度: {len(markdown_text)} 字符）")
    
    # 第二步：使用DeepLX快速翻译
    print("\n⚡ 步骤 2/3: DeepLX快速翻译...")
    
    # 按段落分块翻译（DeepLX对长文本支持较好，可以用较大的块）
    max_chunk_size = 5000  # DeepLX可以处理更大的块
    paragraphs = markdown_text.split('\n\n')
    translated_paragraphs = []
    
    current_chunk = ""
    chunk_count = 0
    total_paragraphs = len(paragraphs)
    image_count = 0
    
    start_time = time.time()
    
    for i, para in enumerate(paragraphs):
        # 跳过图片标记（完整保留，不翻译）
        if para.strip().startswith('![') or para.strip().startswith('<img'):
            translated_paragraphs.append(para)
            image_count += 1
            print(f"  🖼️ 保留图片 {image_count}", flush=True)
            continue
        
        # 累积段落到当前块
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # 翻译当前块
            if current_chunk:
                chunk_count += 1
                print(f"  📝 翻译块 {chunk_count} (长度: {len(current_chunk)} 字符, 进度: {i}/{total_paragraphs} 段落)...", flush=True)
                translated_chunk = translate_with_deeplx(current_chunk)
                translated_paragraphs.append(translated_chunk)
                time.sleep(Config.DEEPLX_RATE_LIMIT)
            
            # 开始新块
            current_chunk = para
    
    # 翻译最后一块
    if current_chunk:
        chunk_count += 1
        print(f"  📝 翻译块 {chunk_count} (长度: {len(current_chunk)} 字符)...", flush=True)
        translated_chunk = translate_with_deeplx(current_chunk)
        translated_paragraphs.append(translated_chunk)
    
    deeplx_result = "\n\n".join(translated_paragraphs)
    deeplx_time = time.time() - start_time
    
    print(f"✓ DeepLX翻译完成！共 {chunk_count} 块，耗时 {deeplx_time:.1f} 秒")
    print(f"  原文长度: {len(markdown_text)} 字符")
    print(f"  译文长度: {len(deeplx_result)} 字符")
    print(f"  保留图片: {image_count} 张")
    
    # 第三步：使用AI修正数学公式
    print("\n🔧 步骤 3/3: AI修正数学公式...")
    
    # 分块修正（避免超长文本）
    max_fix_chunk_size = 4000
    
    if len(deeplx_result) <= max_fix_chunk_size:
        print(f"  文本适中，一次性修正...")
        final_result = fix_formulas_with_ai(deeplx_result, api_url=api_url, api_key=api_key, model=model)
    else:
        print(f"  文本较长，分块修正...")
        fix_paragraphs = deeplx_result.split('\n\n')
        fixed_results = []
        
        current_fix_chunk = ""
        fix_chunk_count = 0
        
        for para in fix_paragraphs:
            if len(current_fix_chunk) + len(para) + 2 <= max_fix_chunk_size:
                if current_fix_chunk:
                    current_fix_chunk += "\n\n" + para
                else:
                    current_fix_chunk = para
            else:
                if current_fix_chunk:
                    fix_chunk_count += 1
                    print(f"  🔧 修正块 {fix_chunk_count} (长度: {len(current_fix_chunk)} 字符)...", flush=True)
                    fixed_chunk = fix_formulas_with_ai(current_fix_chunk, api_url=api_url, api_key=api_key, model=model)
                    fixed_results.append(fixed_chunk)
                    time.sleep(0.5)
                
                current_fix_chunk = para
        
        # 修正最后一块
        if current_fix_chunk:
            fix_chunk_count += 1
            print(f"  🔧 修正块 {fix_chunk_count} (长度: {len(current_fix_chunk)} 字符)...", flush=True)
            fixed_chunk = fix_formulas_with_ai(current_fix_chunk, api_url=api_url, api_key=api_key, model=model)
            fixed_results.append(fixed_chunk)
        
        final_result = "\n\n".join(fixed_results)
        print(f"✓ 公式修正完成！共修正 {fix_chunk_count} 块")
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"🎉 混合翻译完成！总耗时: {total_time:.1f} 秒")
    print(f"   DeepLX翻译: {deeplx_time:.1f} 秒 ({deeplx_time/total_time*100:.1f}%)")
    print(f"   AI公式修正: {total_time - deeplx_time:.1f} 秒 ({(total_time - deeplx_time)/total_time*100:.1f}%)")
    print("=" * 60 + "\n")
    
    return final_result


def translate_markdown_content(markdown_text):
    """翻译Markdown内容，保留格式（纯DeepLX模式）"""
    # 先清理整个文本的Unicode字符
    markdown_text = clean_unicode_characters(markdown_text, debug=False)
    
    lines = markdown_text.split('\n')
    translated_lines = []
    
    for line in lines:
        # 跳过空行
        if not line.strip():
            translated_lines.append(line)
            continue
        
        # 跳过代码块标记
        if line.strip().startswith('```'):
            translated_lines.append(line)
            continue
        
        # 跳过图片标记（保留原样）
        if line.strip().startswith('![') or line.strip().startswith('<img'):
            translated_lines.append(line)
            continue
        
        # 翻译其他内容
        translated_line = translate_with_deeplx(line)
        # 翻译后的内容也清理一下
        translated_line = clean_unicode_characters(translated_line, debug=False)
        translated_lines.append(translated_line)
        time.sleep(0.5)  # 避免API限流
    
    return '\n'.join(translated_lines)


def check_translation_completeness(original, translated):
    """检查翻译是否完整"""
    import re
    
    # 统计原文中的英文单词数（粗略估计）
    original_words = len(re.findall(r'\b[a-zA-Z]+\b', original))
    
    # 统计翻译后剩余的英文单词数
    translated_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', translated))  # 4个字母以上的英文单词
    
    # 如果翻译后还有大量英文单词（超过原文的30%），可能不完整
    if original_words > 0 and translated_words > original_words * 0.3:
        return False, translated_words, original_words
    
    return True, translated_words, original_words


def clean_html_tags(text):
    """清理HTML标签并转换为Unicode字符"""
    import re
    
    # 上标数字映射
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
        ',': ','  # 逗号保持不变
    }
    
    # 下标数字映射
    subscripts = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎'
    }
    
    # 处理 <sup>...</sup> 标签
    def replace_sup(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += superscripts.get(char, char)
        return result
    
    text = re.sub(r'<sup>([^<]+)</sup>', replace_sup, text, flags=re.IGNORECASE)
    
    # 处理 <sub>...</sub> 标签
    def replace_sub(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += subscripts.get(char, char)
        return result
    
    text = re.sub(r'<sub>([^<]+)</sub>', replace_sub, text, flags=re.IGNORECASE)
    
    # 移除其他常见的HTML标签但保留内容
    text = re.sub(r'</?b>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?i>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?strong>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?em>', '', text, flags=re.IGNORECASE)
    
    return text


def clean_unicode_characters(text, debug=False):
    """清理文本中无法显示的Unicode字符"""
    from config import Config
    import unicodedata
    
    original_text = text
    
    # 第一步：应用配置中的字符替换规则
    for old_char, new_char in Config.UNICODE_REPLACEMENTS.items():
        text = text.replace(old_char, new_char)
    
    # 第二步：查找并处理剩余的问题字符
    cleaned_text = []
    removed_chars = set()
    
    for char in text:
        code_point = ord(char)
        
        # REPLACEMENT CHARACTER (U+FFFD) 是显示方框的主要原因
        if code_point == 0xFFFD:
            removed_chars.add((char, code_point, 'REPLACEMENT CHARACTER'))
            continue
        
        # 私有使用区字符通常无法显示
        if (0xE000 <= code_point <= 0xF8FF or  # 私有使用区
            0xF0000 <= code_point <= 0xFFFFD or  # 补充私有使用区-A
            0x100000 <= code_point <= 0x10FFFD):  # 补充私有使用区-B
            try:
                char_name = unicodedata.name(char, f'PRIVATE_USE_U+{code_point:04X}')
            except:
                char_name = f'PRIVATE_USE_U+{code_point:04X}'
            removed_chars.add((char, code_point, char_name))
            continue
        
        # 控制字符（除了常见的换行、制表符等）
        if (0x00 <= code_point <= 0x1F and 
            code_point not in [0x09, 0x0A, 0x0D]):  # 保留tab, LF, CR
            removed_chars.add((char, code_point, 'CONTROL_CHARACTER'))
            continue
        
        # 保留其他字符
        cleaned_text.append(char)
    
    result = ''.join(cleaned_text)
    
    # 打印调试信息
    if debug:
        if removed_chars:
            print(f"⚠️ 清理文本时移除了 {len(removed_chars)} 种问题字符:", flush=True)
            for char, code, name in list(removed_chars)[:20]:  # 最多显示20个
                print(f"  '{char}' | U+{code:04X} | {name}", flush=True)
        else:
            print("✓ 没有发现需要移除的问题字符", flush=True)
        
        # 统计被替换的字符
        replaced_count = 0
        for old_char in Config.UNICODE_REPLACEMENTS.keys():
            if old_char in original_text:
                replaced_count += original_text.count(old_char)
        if replaced_count > 0:
            print(f"✓ 替换了 {replaced_count} 个特殊Unicode字符", flush=True)
    
    # 如果文本有变化，打印简要信息
    elif result != original_text:
        print(f"✓ 清理了文本中的特殊字符", flush=True)
    
    return result


def convert_latex_to_unicode(text):
    """将常见的 LaTeX 数学符号转换为 Unicode"""
    original_text = text  # 保存原始文本用于调试
    
    # 上标数字映射
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾'
    }
    
    # 下标数字映射
    subscripts = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎'
    }
    
    # 希腊字母映射
    greek_letters = {
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
        r'\Delta': 'Δ', r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η',
        r'\theta': 'θ', r'\Theta': 'Θ', r'\lambda': 'λ', r'\Lambda': 'Λ',
        r'\mu': 'μ', r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π', r'\Pi': 'Π',
        r'\rho': 'ρ', r'\sigma': 'σ', r'\Sigma': 'Σ', r'\tau': 'τ',
        r'\phi': 'φ', r'\Phi': 'Φ', r'\chi': 'χ', r'\psi': 'ψ', r'\Psi': 'Ψ',
        r'\omega': 'ω', r'\Omega': 'Ω'
    }
    
    # 其他常用符号
    symbols = {
        r'\sim': '∼', r'\approx': '≈', r'\pm': '±', r'\times': '×',
        r'\div': '÷', r'\leq': '≤', r'\geq': '≥', r'\neq': '≠',
        r'\infty': '∞', r'\sum': '∑', r'\prod': '∏', r'\int': '∫',
        r'\partial': '∂', r'\nabla': '∇', r'\cdot': '·'
    }
    
    # 首先处理希腊字母和符号
    for latex, unicode_char in greek_letters.items():
        text = text.replace(latex, unicode_char)
    for latex, unicode_char in symbols.items():
        text = text.replace(latex, unicode_char)
    
    # 处理上标 ^{...}
    def replace_superscript(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += superscripts.get(char, char)
        return result
    
    text = re.sub(r'\^{([^}]+)}', replace_superscript, text)
    
    # 处理简单上标 ^x
    def replace_simple_superscript(match):
        char = match.group(1)
        return superscripts.get(char, '^' + char)
    
    text = re.sub(r'\^([0-9+-])', replace_simple_superscript, text)
    
    # 处理下标 _{...}
    def replace_subscript(match):
        content = match.group(1)
        result = ''
        for char in content:
            result += subscripts.get(char, char)
        return result
    
    text = re.sub(r'_{([^}]+)}', replace_subscript, text)
    
    # 处理简单下标 _x
    def replace_simple_subscript(match):
        char = match.group(1)
        return subscripts.get(char, '_' + char)
    
    text = re.sub(r'_([0-9+-])', replace_simple_subscript, text)
    
    # 处理 \mathrm{...}
    text = re.sub(r'\\mathrm{([^}]+)}', r'\1', text)
    
    # 移除剩余的反斜杠命令
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # 移除多余的花括号
    text = text.replace('{', '').replace('}', '')
    
    # 清理可能残留的问题Unicode字符
    text = clean_unicode_characters(text, debug=False)
    
    # 如果转换有变化，打印调试信息
    if text != original_text:
        print(f"✓ 公式转换: '{original_text}' → '{text}'")
    
    return text


def markdown_to_pdf(markdown_text, output_path):
    """将Markdown转换为PDF"""
    import sys
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    
    # 在开始处理前，先进行一次完整的字符清理（启用调试）
    print("\n" + "="*50, flush=True)
    print("开始清理Markdown文本中的问题字符...", flush=True)
    print(f"原始文本长度: {len(markdown_text)}", flush=True)
    print("="*50, flush=True)
    sys.stdout.flush()
    
    markdown_text = clean_unicode_characters(markdown_text, debug=True)
    
    print(f"清理后文本长度: {len(markdown_text)}", flush=True)
    print("="*50 + "\n", flush=True)
    sys.stdout.flush()
    
    # 创建PDF文档
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    # 注册字体 - 优先使用支持完整 Unicode 的字体
    font_registered = False

    # 允许通过环境/配置或项目内 fonts 目录挂载字体，以便在精简容器（如 Zeabur）中避免乱码
    local_font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_paths = []

    # 用户自定义路径优先（可通过环境变量 PDF_FONT_PATH 覆盖 Config.PDF_FONT_PATH）
    custom_font_path = os.environ.get('PDF_FONT_PATH') or Config.PDF_FONT_PATH
    if custom_font_path:
        font_paths.append(custom_font_path)
        print(f"自定义字体路径: {custom_font_path}", flush=True)

    # 项目内置/挂载字体目录（需要自行放置字体文件）
    # 注意：ReportLab 只支持 TrueType 格式(.ttf)，不支持 PostScript outlines (.otf CFF)
    if os.path.isdir(local_font_dir):
        for candidate in [
            'Arial-Unicode.ttf',  # 本地开发用的符号链接
            'NotoSansCJKsc-Regular.ttf',  # 完整版 TrueType (推荐)
            'NotoSansSC-Regular.ttf',  # Google Fonts 版本 TrueType
            'SourceHanSansCN-Regular.ttf',  # 思源黑体 TrueType
            'DejaVuSans.ttf', 'DejaVuSansMono.ttf'
        ]:
            font_paths.append(os.path.join(local_font_dir, candidate))

    # 系统常见字体 - 优先级：覆盖 Unicode 的字体优先
    font_paths.extend([
        # macOS 字体 - Arial Unicode MS 支持最完整的 Unicode
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        # macOS 其他支持广泛 Unicode 的字体
        '/System/Library/Fonts/Apple Symbols.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        # 然后是中文字体
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        # Linux 字体
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf',
        # Windows 字体
        'C:\\Windows\\Fonts\\Arial.ttf',
        'C:\\Windows\\Fonts\\arialuni.ttf',
        'C:\\Windows\\Fonts\\simhei.ttf',
        'C:\\Windows\\Fonts\\simsun.ttc',
    ])

    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                font_registered = True
                print(f"✓ 成功注册字体: {font_path}")
                font_name = 'UnicodeFont'
                break
        except Exception as e:
            print(f"⚠️ 无法注册字体 {font_path}: {e}")
            continue
    
    # 如果无法注册TrueType字体，使用内置的CID字体
    if not font_registered:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            font_name = 'STSong-Light'
            print("✓ 使用内置CID字体: STSong-Light")
        except:
            try:
                pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
                font_name = 'HeiseiMin-W3'
                print("✓ 使用内置CID字体: HeiseiMin-W3")
            except:
                font_name = 'Helvetica'
                print("⚠️ 无法加载Unicode字体，使用默认字体（可能无法显示特殊符号）")

    # 尝试注册“符号/上、下标”备用字体，并在段落内对缺字字符进行按需切换
    fallback_font_name = None
    fallback_candidates = []
    if os.path.isdir(local_font_dir):
        fallback_candidates.extend([
            os.path.join(local_font_dir, 'NotoSansMath-Regular.otf'),
            os.path.join(local_font_dir, 'NotoSansMath-Regular.ttf'),
            os.path.join(local_font_dir, 'DejaVuSans.ttf'),
            os.path.join(local_font_dir, 'NotoSansSymbols2-Regular.ttf'),
        ])
    fallback_candidates.extend([
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansMath-Regular.otf',
        '/usr/share/fonts/opentype/noto/NotoSansMath-Regular.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansSymbols2-Regular.ttf',
        '/Library/Fonts/DejaVuSans.ttf',
    ])

    for fp in fallback_candidates:
        try:
            if os.path.exists(fp):
                pdfmetrics.registerFont(TTFont('UnicodeFallback', fp))
                fallback_font_name = 'UnicodeFallback'
                print(f"✓ 成功注册备用字体: {fp}")
                break
        except Exception as e:
            print(f"⚠️ 无法注册备用字体 {fp}: {e}")
            continue

    # 包装一个工具：对文本中上/下标字符用备用字体渲染，避免缺字形
    import html as _html
    def _escape_html(s: str) -> str:
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def _apply_supsub_fallback(s: str) -> str:
        t = _escape_html(s)
        if not fallback_font_name:
            return t
        def need_fallback(cp: int) -> bool:
            # 上/下标
            if cp in (0x00B2, 0x00B3, 0x00B9) or 0x2070 <= cp <= 0x209F or 0x2080 <= cp <= 0x208E:
                return True
            # 希腊字母
            if 0x0370 <= cp <= 0x03FF:
                return True
            # 数学和技术符号常见区段
            if 0x2100 <= cp <= 0x214F:
                return True
            if 0x2190 <= cp <= 0x21FF:
                return True
            if 0x2200 <= cp <= 0x22FF:
                return True
            if 0x25A0 <= cp <= 0x25FF:
                return True
            return False
        out = []
        open_tag = False
        for ch in t:
            cp = ord(ch)
            if need_fallback(cp):
                if not open_tag:
                    out.append(f'<font name="{fallback_font_name}">')
                    open_tag = True
                out.append(ch)
            else:
                if open_tag:
                    out.append('</font>')
                    open_tag = False
                out.append(ch)
        if open_tag:
            out.append('</font>')
        return ''.join(out)
    
    # 创建中文样式
    chinese_style = ParagraphStyle(
        'Chinese',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        wordWrap='CJK',
    )
    chinese_title = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=20,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    chinese_heading1 = ParagraphStyle(
        'ChineseHeading1',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        leading=22,
        spaceAfter=12,
        spaceBefore=12,
    )
    chinese_heading2 = ParagraphStyle(
        'ChineseHeading2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        leading=20,
        spaceAfter=10,
        spaceBefore=10,
    )
    
    # 处理Markdown文本
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 0.15*inch))
            continue
        
        # 处理标题
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            
            # 清理Unicode字符（标题已在整体清理过，这里不需要再次清理）
            # text = clean_unicode_characters(text, debug=False)
            
            # 处理数学公式
            def replace_math(match):
                latex = match.group(1)
                return convert_latex_to_unicode(latex)
            
            text = re.sub(r'\$([^\$]+)\$', replace_math, text)
            text = re.sub(r'\$\$([^\$]+)\$\$', replace_math, text)
            
            # HTML转义 + 对上/下标字符应用备用字体
            text = _apply_supsub_fallback(text)
            
            if level == 1:
                p = Paragraph(text, chinese_title)
                story.append(p)
                story.append(Spacer(1, 0.3*inch))
            elif level == 2:
                p = Paragraph(text, chinese_heading1)
                story.append(p)
                story.append(Spacer(1, 0.2*inch))
            else:
                p = Paragraph(text, chinese_heading2)
                story.append(p)
                story.append(Spacer(1, 0.15*inch))
        else:
            # 处理图片标记
            if line.startswith('!['):
                try:
                    # 匹配 Markdown 图片语法: ![alt](url)
                    match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
                    if match:
                        alt_text = match.group(1)
                        image_data = match.group(2)
                        
                        # 检查是否是 base64 图片
                        if image_data.startswith('data:image'):
                            # 提取 base64 数据
                            base64_match = re.search(r'base64,(.+)', image_data)
                            if base64_match:
                                base64_str = base64_match.group(1)
                                try:
                                    img_data = base64.b64decode(base64_str)
                                    img_buffer = BytesIO(img_data)
                                    img = Image(img_buffer)
                                    
                                    # 调整图片大小以适应页面
                                    max_width = 6*inch
                                    max_height = 8*inch
                                    if img.drawWidth > max_width:
                                        ratio = max_width / img.drawWidth
                                        img.drawWidth = max_width
                                        img.drawHeight = img.drawHeight * ratio
                                    if img.drawHeight > max_height:
                                        ratio = max_height / img.drawHeight
                                        img.drawHeight = max_height
                                        img.drawWidth = img.drawWidth * ratio
                                    
                                    story.append(img)
                                    story.append(Spacer(1, 0.1*inch))
                                    print(f"✓ 成功添加图片: {alt_text}")
                                except Exception as e:
                                    print(f"⚠️ 处理base64图片失败: {e}")
                                    # 添加图片说明作为替代
                                    if alt_text:
                                        # alt文本已在整体清理过
                                        p = Paragraph(f"[图片: {alt_text}]", chinese_style)
                                        story.append(p)
                        else:
                            # URL 图片（暂不支持，显示说明）
                            if alt_text:
                                # alt文本已在整体清理过
                                p = Paragraph(f"[图片: {alt_text}]", chinese_style)
                                story.append(p)
                                story.append(Spacer(1, 0.08*inch))
                except Exception as e:
                    print(f"⚠️ 处理图片行出错: {e}, 内容: {line[:100]}...")
                continue
            
            # 跳过 HTML img 标签（可能需要额外处理）
            if line.startswith('<img'):
                print(f"⚠️ 跳过 HTML img 标签: {line[:100]}...")
                continue
            
            # 处理普通文本
            text = line
            
            # 清理Unicode字符（文本已在整体清理过，这里不需要再次清理）
            # text = clean_unicode_characters(text, debug=False)
            
            # 处理数学公式 $...$ 和 $$...$$
            def replace_math(match):
                latex = match.group(1)
                return convert_latex_to_unicode(latex)
            
            # 先处理行内公式 $...$
            text = re.sub(r'\$([^\$]+)\$', replace_math, text)
            
            # 处理行间公式 $$...$$（通常单独一行）
            text = re.sub(r'\$\$([^\$]+)\$\$', replace_math, text)
            
            # HTML转义 + 对上/下标字符应用备用字体（在公式转换之后）
            text = _apply_supsub_fallback(text)
            
            # 处理Markdown格式
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # 粗体
            text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)  # 斜体
            text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)  # 代码
            
            if text.strip():
                try:
                    p = Paragraph(text, chinese_style)
                    story.append(p)
                    story.append(Spacer(1, 0.08*inch))
                except Exception as e:
                    print(f"⚠️ 处理段落出错: {e}, 文本: {text[:50]}...")
                    continue
    
    # 生成PDF
    try:
        doc.build(story)
        print(f"✓ PDF生成成功: {output_path}")
    except Exception as e:
        print(f"❌ PDF生成失败: {e}")
        raise


@app.route('/')
def index():
    """主页 - 直接显示完整界面"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>模板加载错误</h1><p>{str(e)}</p>"

@app.route('/full')
def full():
    """完整界面"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>模板加载错误</h1><p>{str(e)}</p>"

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'running',
        'message': 'PDF翻译器服务正常',
        'timestamp': time.time()
    })

@app.route('/test')
def test():
    """测试路由"""
    return jsonify({'status': 'ok', 'message': 'PDF翻译器运行正常'})


@app.route('/translate', methods=['POST'])
def translate_pdf():
    """处理PDF翻译请求"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': '只支持PDF文件'}), 400
    
    try:
        # 保存上传的文件
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(upload_path)

        # 解析 MinerU 配置
        mineru_options = {
            "is_ocr": _to_bool(request.form.get('is_ocr'), True),
            "include_image_base64": _to_bool(request.form.get('include_image_base64'), True),
            "formula_enable": _to_bool(request.form.get('formula_enable'), True),
            "table_enable": _to_bool(request.form.get('table_enable'), True),
            "layout_model": request.form.get('layout_model', 'doclayout_yolo'),
            "output_format": request.form.get('output_format', 'md'),
        }

        end_pages_input = request.form.get('end_pages')
        print(f"从前端接收到的 end_pages: '{end_pages_input}'")
        if end_pages_input and end_pages_input.strip():
            # end_pages 是处理到第几页为止的数字
            mineru_options['end_pages'] = end_pages_input.strip()
            print(f"✓ 设置 end_pages = '{end_pages_input.strip()}' (处理第1页到第{end_pages_input.strip()}页)")

        language = request.form.get('language')
        if language:
            mineru_options['language'] = language.strip()
        
        # 获取前端传来的API配置
        parse_api_token = request.form.get('parse_api_token')
        translate_api_url = request.form.get('translate_api_url')
        translate_api_key = request.form.get('translate_api_key')
        translate_api_model = request.form.get('translate_api_model')
        
        # 打印API配置信息（用于调试）
        print("\n" + "=" * 50)
        print("API配置信息:")
        if parse_api_token:
            print(f"✓ 使用自定义解析API Token: {parse_api_token[:10]}...")
        else:
            print("  使用默认解析API配置")
        
        if translate_api_url:
            print(f"✓ 使用自定义翻译API URL: {translate_api_url}")
        else:
            print("  使用默认翻译API URL")
            
        if translate_api_key:
            print(f"✓ 使用自定义翻译API Key: {translate_api_key[:10]}...")
        else:
            print("  使用默认翻译API Key")
            
        if translate_api_model:
            print(f"✓ 使用自定义翻译模型: {translate_api_model}")
        else:
            print("  使用默认翻译模型")
        print("=" * 50 + "\n")
        
        # 1. 使用MinerU解析PDF
        print("正在解析PDF...")
        result = parse_pdf_with_mineru(upload_path, mineru_options, api_token=parse_api_token)
        task_id = result.get("task_id")
        
        if not task_id:
            return jsonify({'error': 'MinerU任务创建失败'}), 500
        
        print(f"任务ID: {task_id}")
        
        # 2. 等待MinerU处理完成
        print("等待MinerU处理...")
        task_result = poll_mineru_task(task_id, api_token=parse_api_token)
        
        # 3. 获取解析结果
        if task_result.get("status") != "success":
            return jsonify({'error': 'PDF解析失败'}), 500
        
        # 保存任务结果用于调试
        print(f"任务结果: {json.dumps(task_result, indent=2, ensure_ascii=False)}")
        
        # 获取Markdown内容
        markdown_content = None
        if "output" in task_result:
            output = task_result["output"]
            
            # 尝试从 segments 获取内容
            if "segments" in output and isinstance(output["segments"], list):
                segments = output["segments"]
                print(f"✓ 找到 {len(segments)} 个内容段")
                
                # 合并所有segments的content
                content_parts = []
                for segment in segments:
                    if "content" in segment:
                        content_parts.append(segment["content"])
                
                if content_parts:
                    markdown_content = "\n\n".join(content_parts)
                    print(f"✓ 从 segments 获取内容，总长度: {len(markdown_content)}")
                else:
                    print("⚠️ segments中没有content字段")
            
            # 尝试获取 text_result
            elif "text_result" in output:
                markdown_content = output["text_result"]
                print("✓ 从 text_result 获取内容")
            
            # 尝试下载 file_url
            elif "file_url" in output:
                file_url = output["file_url"]
                print(f"下载文件: {file_url}")
                response = requests.get(file_url, timeout=30)
                markdown_content = response.text
                print(f"✓ 下载内容长度: {len(markdown_content)}")
            
            # 尝试获取 content 字段
            elif "content" in output:
                markdown_content = output["content"]
                print("✓ 从 content 获取内容")
            
            else:
                print(f"⚠️ output 字段不包含预期的内容，字段列表: {list(output.keys())}")
        else:
            print("⚠️ 任务结果中没有 output 字段")
        
        if not markdown_content:
            error_msg = f'无法获取解析内容。任务结果: {json.dumps(task_result, ensure_ascii=False)}'
            print(error_msg)
            return jsonify({'error': '无法获取解析内容，请查看服务器日志'}), 500
        
        # 保存任务结果到文件
        task_file = os.path.join(app.config['UPLOAD_FOLDER'], f"task_{task_id}.json")
        with open(task_file, "w", encoding='utf-8') as f:
            json.dump(task_result, f, indent=4, ensure_ascii=False)
        print(f"✓ 任务结果已保存到: {task_file}")
        
        # 保存原始 Markdown 内容到文件
        markdown_file = os.path.join(app.config['UPLOAD_FOLDER'], f"markdown_{task_id}.md")
        with open(markdown_file, "w", encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ 原始Markdown已保存到: {markdown_file}")
        print(f"✓ Markdown内容长度: {len(markdown_content)}")
        
        print("PDF解析成功！")
        
        # 4. 根据翻译模式选择翻译方法
        translation_mode = request.form.get('translation_mode', 'hybrid')  # 默认使用混合模式
        
        print("\n" + "="*50)
        print(f"翻译模式: {translation_mode}")
        print("="*50)
        
        if translation_mode == 'hybrid':
            # 混合模式：DeepLX + AI公式修正（推荐，快速且准确）
            print("使用混合翻译模式（DeepLX快速翻译 + AI公式修正）")
            translated_content = translate_markdown_hybrid(
                markdown_content,
                api_url=translate_api_url,
                api_key=translate_api_key,
                model=translate_api_model
            )
        elif translation_mode == 'ai':
            # 纯AI模式：质量最高但速度慢
            print("使用纯AI翻译模式（高质量但较慢）")
            translated_content = translate_markdown_content_with_ai(
                markdown_content,
                api_url=translate_api_url,
                api_key=translate_api_key,
                model=translate_api_model
            )
        elif translation_mode == 'deeplx':
            # 纯DeepLX模式：速度最快但公式可能有问题
            print("使用纯DeepLX翻译模式（最快但公式可能需手动修正）")
            translated_content = translate_markdown_content(markdown_content)
        else:
            # 默认使用混合模式
            print("未知翻译模式，使用默认混合模式")
            translated_content = translate_markdown_hybrid(
                markdown_content,
                api_url=translate_api_url,
                api_key=translate_api_key,
                model=translate_api_model
            )
        
        print("="*50)
        print("✓ 翻译完成！\n")
        
        # 保存翻译后的内容
        translated_file = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{task_id}.md")
        with open(translated_file, "w", encoding='utf-8') as f:
            f.write(translated_content)
        print(f"✓ 翻译后的Markdown已保存到: {translated_file}")
        
        print("生成PDF...")
        
        # 5. 生成翻译后的PDF
        output_filename = f"translated_{os.path.splitext(file.filename)[0]}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        markdown_to_pdf(translated_content, output_path)
        
        print("PDF生成成功！")
        
        # 6. 返回文件
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # 清理临时文件
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
        except:
            pass


if __name__ == '__main__':
    print("启动PDF翻译器...")
    print("访问 http://localhost:8000 使用应用")
    app.run(debug=False, host='0.0.0.0', port=8000)
