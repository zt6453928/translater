#!/bin/bash
# 下载 Noto Sans CJK SC 字体的脚本

set -e

FONT_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_FILE="$FONT_DIR/NotoSansCJKsc-Regular.otf"

echo "======================================"
echo "下载 Noto Sans CJK SC 字体"
echo "======================================"
echo ""

# 尝试多个下载源
URLS=(
    "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
    "https://ghproxy.com/https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
    "https://mirror.ghproxy.com/https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
)

SUCCESS=0

for url in "${URLS[@]}"; do
    echo "尝试从: $url"
    if curl -L -o "$FONT_FILE" "$url" 2>/dev/null; then
        if [ -f "$FONT_FILE" ] && [ -s "$FONT_FILE" ]; then
            SIZE=$(du -h "$FONT_FILE" | cut -f1)
            echo "✓ 下载成功! 文件大小: $SIZE"
            echo "✓ 保存位置: $FONT_FILE"
            SUCCESS=1
            break
        fi
    fi
    echo "✗ 下载失败，尝试下一个源..."
    echo ""
done

if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "自动下载失败，请手动下载："
    echo "======================================"
    echo ""
    echo "1. 访问以下任一网址下载字体："
    echo "   • https://fonts.google.com/noto/specimen/Noto+Sans+SC"
    echo "   • https://github.com/googlefonts/noto-cjk/releases"
    echo ""
    echo "2. 下载文件: NotoSansCJKsc-Regular.otf"
    echo ""
    echo "3. 将字体文件复制到:"
    echo "   $FONT_DIR/"
    echo ""
    exit 1
fi

echo ""
echo "======================================"
echo "字体安装完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 在 Zeabur 环境变量中设置:"
echo "   PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf"
echo ""
echo "2. 或者在 config.py 中设置:"
echo "   PDF_FONT_PATH = \"$FONT_FILE\""
echo ""
