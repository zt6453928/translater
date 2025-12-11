"""
配置文件
用于管理应用程序的各种配置参数
"""

import os

class Config:
    """基础配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # MinerU API配置
    MINERU_API_URL = "https://ai.gitee.com/v1/async/documents/parse"
    MINERU_API_TOKEN = os.environ.get('MINERU_API_TOKEN') or "V5PWW7GYB8NOTZGQ6EEF4IJL3TIGXJF3YU2L371P"
    MINERU_TIMEOUT = 30 * 60  # 30分钟
    MINERU_RETRY_INTERVAL = 5  # 5秒
    
    # MinerU 解析参数
    MINERU_PARAMS = {
        "model": "MinerU2.5",
        "is_ocr": True,
        "include_image_base64": True,
        "formula_enable": True,
        "table_enable": True,
        "layout_model": "doclayout_yolo",
        "output_format": "md"
    }
    
    # DeepLX API配置（快速翻译模式）
    DEEPLX_API_URL = os.environ.get('DEEPLX_API_URL') or "https://api.deeplx.org/7cLJfW49zRcsx7lZ9bKjAnoMIGDMXP67_cLUrShX2Ik/translate"
    DEEPLX_TIMEOUT = 30  # 30秒
    DEEPLX_RATE_LIMIT = 0.3  # 每次翻译间隔0.3秒（加快速度）
    DEEPLX_MAX_RETRIES = 3  # DeepLX请求失败时的最大重试次数
    
    # AI翻译API配置（OpenAI兼容接口）
    AI_TRANSLATE_API_URL = os.environ.get('AI_TRANSLATE_API_URL') or "https://b4u.qzz.io/v1/chat/completions"
    AI_TRANSLATE_API_KEY = os.environ.get('AI_TRANSLATE_API_KEY') or "sk-xMADfHsmiaSmJBDVni7f1BDxNdidPFboYf73o7LeOhPxQNOe"
    AI_TRANSLATE_MODEL = os.environ.get('AI_TRANSLATE_MODEL') or "claude-4.5-sonnet-think"
    AI_TRANSLATE_TIMEOUT = 300  # 300秒（5分钟，给思考模型更多时间）
    AI_TRANSLATE_MAX_TOKENS = 16000  # 增加到16000以支持更长的输出
    AI_TRANSLATE_MAX_RETRIES = 3  # API请求失败时的最大重试次数
    AI_TRANSLATE_CHUNK_SIZE = 3000  # 分块翻译时每块的最大字符数（降低以提高稳定性）
    
    # 翻译参数
    TRANSLATION_SOURCE_LANG = "EN"  # 源语言：英文
    TRANSLATION_TARGET_LANG = "ZH"  # 目标语言：中文
    TRANSLATION_MODE = "hybrid"  # 翻译模式：fast(纯AI), hybrid(DeepLX+AI修正), deeplx(纯DeepLX)
    
    # PDF生成配置
    PDF_PAGE_SIZE = "A4"
    PDF_FONT_NAME = "Chinese"  # 中文字体名称
    PDF_FONT_PATH = None  # 留空，让app.py自动选择最佳字体（支持通过环境变量覆盖）
    PDF_FONT_SIZE = 12
    PDF_TITLE_SIZE = 18
    PDF_HEADING_SIZE = 16
    
    # Unicode字符替换映射（处理PDF中无法显示的特殊字符）
    UNICODE_REPLACEMENTS = {
        # 各种空格字符
        '\u00A0': ' ',      # NO-BREAK SPACE
        '\u2009': ' ',      # THIN SPACE
        '\u200A': ' ',      # HAIR SPACE
        '\u200B': '',       # ZERO WIDTH SPACE
        '\u200C': '',       # ZERO WIDTH NON-JOINER
        '\u200D': '',       # ZERO WIDTH JOINER
        '\u202F': ' ',      # NARROW NO-BREAK SPACE
        '\uFEFF': '',       # ZERO WIDTH NO-BREAK SPACE
        '\u2008': ' ',      # PUNCTUATION SPACE
        '\u2003': ' ',      # EM SPACE
        '\u2002': ' ',      # EN SPACE
        '\u3000': ' ',      # IDEOGRAPHIC SPACE
        
        # 特殊字符
        '\u2011': '-',      # NON-BREAKING HYPHEN
        '\u2013': '-',      # EN DASH
        '\u2014': '--',     # EM DASH
        '\u2012': '-',      # FIGURE DASH
        '\u2212': '-',      # MINUS SIGN
        '\u2043': '-',      # HYPHEN BULLET
        '\u223C': '~',      # TILDE OPERATOR
        '\u02DC': '~',      # SMALL TILDE
        '\u2053': '~',      # SWUNG DASH
        '\u301C': '~',      # WAVE DASH
        '\uFE4D': '_',      # DASHED LOW LINE
        '\uFE4E': '_',      # CENTRELINE LOW LINE
        '\uFE4F': '_',      # WAVY LOW LINE
        '\uFF5E': '~',      # FULLWIDTH TILDE
        
        # 引号
        '\u2018': "'",      # LEFT SINGLE QUOTATION MARK
        '\u2019': "'",      # RIGHT SINGLE QUOTATION MARK
        '\u201C': '"',      # LEFT DOUBLE QUOTATION MARK
        '\u201D': '"',      # RIGHT DOUBLE QUOTATION MARK
        '\u201A': ',',      # SINGLE LOW-9 QUOTATION MARK
        '\u201B': "'",      # SINGLE HIGH-REVERSED-9 QUOTATION MARK
        '\u201E': '"',      # DOUBLE LOW-9 QUOTATION MARK
        '\u201F': '"',      # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
        
        # 上标数字（替换为普通数字）
        '\u00B9': '1',      # SUPERSCRIPT ONE ¹
        '\u00B2': '2',      # SUPERSCRIPT TWO ²
        '\u00B3': '3',      # SUPERSCRIPT THREE ³
        '\u2074': '4',      # SUPERSCRIPT FOUR ⁴
        '\u2075': '5',      # SUPERSCRIPT FIVE ⁵
        '\u2076': '6',      # SUPERSCRIPT SIX ⁶
        '\u2077': '7',      # SUPERSCRIPT SEVEN ⁷
        '\u2078': '8',      # SUPERSCRIPT EIGHT ⁸
        '\u2079': '9',      # SUPERSCRIPT NINE ⁹
        '\u2070': '0',      # SUPERSCRIPT ZERO ⁰
        
        # 下标数字（替换为普通数字）
        '\u2080': '0',      # SUBSCRIPT ZERO ₀
        '\u2081': '1',      # SUBSCRIPT ONE ₁
        '\u2082': '2',      # SUBSCRIPT TWO ₂
        '\u2083': '3',      # SUBSCRIPT THREE ₃
        '\u2084': '4',      # SUBSCRIPT FOUR ₄
        '\u2085': '5',      # SUBSCRIPT FIVE ₅
        '\u2086': '6',      # SUBSCRIPT SIX ₆
        '\u2087': '7',      # SUBSCRIPT SEVEN ₇
        '\u2088': '8',      # SUBSCRIPT EIGHT ₈
        '\u2089': '9',      # SUBSCRIPT NINE ₉
        
        # 其他常见问题字符
        '\u00AD': '',       # SOFT HYPHEN
        '\u2022': '*',      # BULLET
        '\u2023': '>',      # TRIANGULAR BULLET
        '\u2024': '.',      # ONE DOT LEADER
        '\u2025': '..',     # TWO DOT LEADER
        '\u2026': '...',    # HORIZONTAL ELLIPSIS
        '\u00B7': '·',      # MIDDLE DOT
        '\u2010': '-',      # HYPHEN
        '\u00B0': '°',      # DEGREE SIGN
        '\u2032': "'",      # PRIME
        '\u2033': '"',      # DOUBLE PRIME
        
        # 不可见或控制字符
        '\uFFFD': '',       # REPLACEMENT CHARACTER (显示为方框的常见原因)
        '\uFFFE': '',       # 非字符
        '\uFFFF': '',       # 非字符
        '\u0000': '',       # NULL
        '\u0009': '\t',     # TAB
        '\u000B': ' ',      # VERTICAL TAB
        '\u000C': ' ',      # FORM FEED
    }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}











