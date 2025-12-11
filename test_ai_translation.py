#!/usr/bin/env python3
"""
测试AI翻译功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import Config

def test_ai_api():
    """测试AI API连接"""
    import requests
    
    print("="*60)
    print("测试AI翻译API连接")
    print("="*60)
    
    print(f"\n配置信息:")
    print(f"  API URL: {Config.AI_TRANSLATE_API_URL}")
    print(f"  模型: {Config.AI_TRANSLATE_MODEL}")
    print(f"  API Key: {Config.AI_TRANSLATE_API_KEY[:20]}...")
    
    # 测试包含作者上标的文本
    test_text = """# Test Article

Haiyang Wang $^{1,2,3}$, Yongbo Peng $^{1,4}$, Chao Li $^{2,3,5}$

This is a test paragraph with math formula: $\\delta^{13}\\mathrm{C}$ and $\\mathrm{O}_2$.

The value is approximately $5.0 \\pm 0.3$ and ranges from $^{12-14}$ to $^{19-21}$.

The isotope composition $\\Delta^{17}\\mathrm{O}$ shows variation over $\\sim 7$ million years.
"""
    
    print(f"\n测试文本:\n{test_text}")
    print("\n开始翻译...")
    
    headers = {
        "Authorization": f"Bearer {Config.AI_TRANSLATE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """你是一个专业的学术论文翻译专家。请将英文学术内容翻译成中文，并严格遵循以下规则：

## 核心要求
1. **翻译质量**：使用准确、流畅的学术中文
2. **完全清除方框字符**：任何方框(□)字符都必须被移除或替换
3. **正确处理参考文献标注**：上标数字之间不要有空格或其他字符

## 数学公式处理
将所有LaTeX数学公式转换为Unicode格式：

### 上标：⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻
- 示例：$^{13}C$ → ¹³C，$^{12-14}$ → ¹²⁻¹⁴，$^{2,18}$ → ²,¹⁸

### 下标：₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉
- 示例：$O_2$ → O₂

### 希腊字母：α β γ δ ε ζ η θ λ μ ν ξ π ρ σ τ φ χ ψ ω Δ Θ Λ Π Σ Φ Ψ Ω

### 数学符号：± × ÷ ≤ ≥ ≠ ≈ ∞ ∑ ∏ ∫ ∂ ∇ · ∼

## 特殊处理
- 作者上标：如 "Wang $^{1,2,3}$" → "Wang ¹,²,³"（数字间只用逗号）
- 波浪号：$\\sim$ → ∼

## 严格禁止
- ❌ 不要使用HTML标签（如 <sup>、<sub>、<b> 等）
- ❌ 不要有方框字符(□)
- ✅ 必须使用Unicode上标下标字符

只返回翻译后的内容。"""
    
    payload = {
        "model": Config.AI_TRANSLATE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_text}
        ],
        "max_tokens": 1000,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            Config.AI_TRANSLATE_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                translated = result["choices"][0]["message"]["content"]
                print("\n✓ 翻译成功！")
                print("\n翻译结果:")
                print("-"*60)
                print(translated)
                print("-"*60)
                return True
            else:
                print(f"\n✗ 响应格式异常: {result}")
                return False
        else:
            print(f"\n✗ API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_api()
    sys.exit(0 if success else 1)
