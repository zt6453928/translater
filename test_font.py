#!/usr/bin/env python3
"""
测试字体加载功能
验证 PDF 生成时中文和数学符号的显示
"""

import os
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

def test_font_loading():
    """测试字体加载"""
    print("="*60)
    print("测试字体加载功能")
    print("="*60)
    print()
    
    # 获取字体路径列表（与 app.py 中的逻辑一致）
    local_font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_paths = []
    
    # 用户自定义路径
    custom_font_path = os.environ.get('PDF_FONT_PATH')
    if custom_font_path:
        font_paths.append(custom_font_path)
        print(f"环境变量 PDF_FONT_PATH: {custom_font_path}")
    
    # 项目内置字体
    if os.path.isdir(local_font_dir):
        for candidate in [
            'NotoSansCJKsc-Regular.otf', 'NotoSansCJKsc-Regular.ttf',
            'NotoSansSC-Regular.otf', 'NotoSansSC-Regular.ttf',
            'SourceHanSansCN-Regular.otf', 'SourceHanSerifCN-Regular.otf',
            'DejaVuSans.ttf', 'DejaVuSansMono.ttf',
            'Arial-Unicode.ttf'
        ]:
            font_paths.append(os.path.join(local_font_dir, candidate))
    
    # 系统字体
    font_paths.extend([
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        '/System/Library/Fonts/PingFang.ttc',
    ])
    
    print(f"\n检查 {len(font_paths)} 个可能的字体路径...\n")
    
    # 尝试加载字体
    font_registered = False
    font_name = None
    loaded_font_path = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"✓ 找到字体文件: {font_path}")
            try:
                # 尝试注册字体
                pdfmetrics.registerFont(TTFont('TestFont', font_path))
                font_registered = True
                font_name = 'TestFont'
                loaded_font_path = font_path
                print(f"  ✓ 成功注册字体: {os.path.basename(font_path)}")
                
                # 获取字体文件大小
                size_mb = os.path.getsize(font_path) / (1024 * 1024)
                print(f"  ✓ 字体文件大小: {size_mb:.2f} MB")
                break
            except Exception as e:
                print(f"  ✗ 注册失败: {e}")
        else:
            # 不打印不存在的路径，避免输出过多
            pass
    
    # 如果无法注册 TrueType 字体，使用内置 CID 字体
    if not font_registered:
        print("\n⚠️  未找到 TrueType/OpenType 字体，尝试内置 CID 字体...")
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            font_name = 'STSong-Light'
            font_registered = True
            print("✓ 使用内置 CID 字体: STSong-Light")
        except:
            print("✗ 无法加载内置 CID 字体")
    
    print()
    print("="*60)
    if font_registered:
        print(f"✅ 字体加载成功: {font_name}")
        if loaded_font_path:
            print(f"   路径: {loaded_font_path}")
    else:
        print("❌ 字体加载失败")
        print("\n建议：")
        print("1. 下载 Noto Sans CJK SC 字体")
        print("2. 放置到 fonts/ 目录")
        print("3. 或设置环境变量 PDF_FONT_PATH")
        return False
    print("="*60)
    print()
    
    return font_name, loaded_font_path

def create_test_pdf(font_name, output_path="test_font_output.pdf"):
    """创建测试 PDF"""
    print("创建测试 PDF 文件...")
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # 设置字体
    c.setFont(font_name, 14)
    
    # 测试内容
    y = height - 50
    
    test_texts = [
        "=" * 50,
        "字体显示测试 Font Display Test",
        "=" * 50,
        "",
        "1. 中文测试：",
        "   这是一段中文文本，用于测试中文字符的显示效果。",
        "   常用汉字：的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞",
        "",
        "2. 数学符号测试：",
        "   基本运算：+ - × ÷ = ≠ ≈ ≤ ≥",
        "   希腊字母：α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω",
        "   上标下标：x² x³ H₂O CO₂",
        "   集合符号：∈ ∉ ⊂ ⊃ ∪ ∩ ∅",
        "   逻辑符号：∀ ∃ ∧ ∨ ¬ ⇒ ⇔",
        "   微积分：∫ ∑ ∏ ∂ ∇ √ ∞",
        "",
        "3. 英文测试：",
        "   The quick brown fox jumps over the lazy dog.",
        "   ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "   abcdefghijklmnopqrstuvwxyz",
        "   0123456789",
        "",
        "4. 特殊字符测试：",
        "   标点符号：，。！？；：""''（）《》【】",
        "   货币符号：￥ $ € £ ¥",
        "   其他符号：@ # % & * © ® ™ § ¶",
        "",
        "=" * 50,
        f"测试完成 - 字体: {font_name}",
        "=" * 50,
    ]
    
    line_height = 20
    for text in test_texts:
        try:
            c.drawString(50, y, text)
            y -= line_height
            
            # 换页
            if y < 50:
                c.showPage()
                c.setFont(font_name, 14)
                y = height - 50
        except Exception as e:
            print(f"  ⚠️  无法渲染文本: {text[:30]}... ({e})")
    
    c.save()
    
    file_size = os.path.getsize(output_path) / 1024
    print(f"✓ 测试 PDF 已生成: {output_path}")
    print(f"  文件大小: {file_size:.2f} KB")
    print()
    print("请打开 PDF 文件检查：")
    print("  - 中文字符是否正确显示")
    print("  - 数学符号是否正确显示")
    print("  - 是否有黑色问号或方框")
    print()

if __name__ == '__main__':
    result = test_font_loading()
    
    if result:
        font_name, font_path = result
        create_test_pdf(font_name)
        print("✅ 字体测试完成！")
        print()
        print("如果 PDF 显示正常，说明字体配置成功。")
        print("如果有乱码，请按照 fonts/README.md 的说明下载字体。")
    else:
        print("❌ 字体测试失败！")
        print()
        print("请查看 fonts/FONT_SETUP.md 获取详细配置说明。")
        sys.exit(1)
