#!/usr/bin/env python3
"""
测试翻译完整性检查
"""

import re

def check_translation_completeness(original, translated):
    """检查翻译是否完整"""
    
    # 统计原文中的英文单词数（粗略估计）
    original_words = len(re.findall(r'\b[a-zA-Z]+\b', original))
    
    # 统计翻译后剩余的英文单词数
    translated_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', translated))  # 4个字母以上的英文单词
    
    # 如果翻译后还有大量英文单词（超过原文的30%），可能不完整
    if original_words > 0 and translated_words > original_words * 0.3:
        return False, translated_words, original_words
    
    return True, translated_words, original_words


def test_completeness():
    """测试完整性检查"""
    
    print("="*70)
    print("测试翻译完整性检查")
    print("="*70)
    
    # 测试用例1：完整翻译
    test1_original = """
    The Ediacaran Period witnessed the largest negative carbonate carbon isotope 
    excursion in Earth's history, known as the Shuram Excursion.
    """
    
    test1_translated = """
    Ediacaran纪见证了地球历史上最大的碳酸盐碳同位素负偏移，
    称为Shuram Excursion (SE)。
    """
    
    is_complete, remaining, original = check_translation_completeness(test1_original, test1_translated)
    print(f"\n测试1 - 完整翻译（保留专有名词）:")
    print(f"  原文单词数: {original}")
    print(f"  残留单词数: {remaining}")
    print(f"  完整性: {'✅ 通过' if is_complete else '❌ 不完整'}")
    
    # 测试用例2：不完整翻译
    test2_original = """
    The Ediacaran Period witnessed the largest negative carbonate carbon isotope 
    excursion in Earth's history, known as the Shuram Excursion.
    
    A sustained oxidation of organics over 7 million years during the SE requires 
    a consistent supply of oxidant, if it is indeed an oceanic oxygenation event.
    """
    
    test2_translated = """
    Ediacaran纪见证了地球历史上最大的碳酸盐碳同位素负偏移，
    称为Shuram Excursion (SE)。
    
    A sustained oxidation of organics over 7 million years during the SE requires 
    a consistent supply of oxidant, if it is indeed an oceanic oxygenation event.
    """
    
    is_complete, remaining, original = check_translation_completeness(test2_original, test2_translated)
    print(f"\n测试2 - 不完整翻译（第二段未翻译）:")
    print(f"  原文单词数: {original}")
    print(f"  残留单词数: {remaining}")
    print(f"  完整性: {'✅ 通过' if is_complete else '❌ 不完整'}")
    
    # 测试用例3：部分翻译
    test3_original = """
    The Ediacaran Period (635-539 Ma) witnessed the largest negative carbonate 
    carbon isotope excursion.
    """
    
    test3_translated = """
    Ediacaran纪(635-539 Ma)见证了地球历史上最大的碳酸盐碳同位素负偏移。
    """
    
    is_complete, remaining, original = check_translation_completeness(test3_original, test3_translated)
    print(f"\n测试3 - 完整翻译（包含专有名词和数字）:")
    print(f"  原文单词数: {original}")
    print(f"  残留单词数: {remaining}")
    print(f"  完整性: {'✅ 通过' if is_complete else '❌ 不完整'}")
    
    print("\n" + "="*70)
    print("说明:")
    print("  - 专有名词（如 Ediacaran, Shuram）保留是正常的")
    print("  - 数字和单位（如 Ma）保留是正常的")
    print("  - 如果有大段普通英文单词未翻译，则判定为不完整")
    print("="*70)


if __name__ == "__main__":
    test_completeness()
