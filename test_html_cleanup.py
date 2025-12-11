#!/usr/bin/env python3
"""
测试HTML标签清理功能
"""

def clean_html_tags(text):
    """清理HTML标签并转换为Unicode字符"""
    import re
    
    # 上标数字映射
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
        ',': ','
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


def test_html_cleanup():
    """测试HTML标签清理"""
    
    test_cases = [
        {
            "input": "海水<sup>12-14</sup>、陆地上暴露的化石有机质<sup>15</sup>",
            "expected": "海水¹²⁻¹⁴、陆地上暴露的化石有机质¹⁵"
        },
        {
            "input": "甲烷<sup>16</sup>。SE的开始紧接着出现了首批大型、明确的后生动物化石<sup>17</sup>",
            "expected": "甲烷¹⁶。SE的开始紧接着出现了首批大型、明确的后生动物化石¹⁷"
        },
        {
            "input": "在SE期间持续约7百万年(Myrs)<sup>2,18</sup>",
            "expected": "在SE期间持续约7百万年(Myrs)²,¹⁸"
        },
        {
            "input": "S-U-TI同位素组成<sup>13-15,19-21</sup>以及页岩中的铁组分<sup>22</sup>",
            "expected": "S-U-TI同位素组成¹³⁻¹⁵,¹⁹⁻²¹以及页岩中的铁组分²²"
        },
        {
            "input": "O<sub>2</sub>和/或硫酸盐浓度上升",
            "expected": "O₂和/或硫酸盐浓度上升"
        },
        {
            "input": "全球碳扰动<sup>23</sup>",
            "expected": "全球碳扰动²³"
        }
    ]
    
    print("="*70)
    print("测试HTML标签清理功能")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        result = clean_html_tags(test["input"])
        success = result == test["expected"]
        
        if success:
            passed += 1
            print(f"\n✅ 测试 {i}: 通过")
        else:
            failed += 1
            print(f"\n❌ 测试 {i}: 失败")
        
        print(f"   输入:    {test['input']}")
        print(f"   期望:    {test['expected']}")
        print(f"   实际:    {result}")
        
        if not success:
            print(f"   差异: 结果不匹配")
    
    print("\n" + "="*70)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = test_html_cleanup()
    sys.exit(0 if success else 1)
