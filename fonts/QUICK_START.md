# 字体配置快速开始

## 🚀 本地开发（已完成）

✅ **本地环境已配置完毕，开箱即用！**

字体已自动链接到系统的 Arial Unicode 字体，支持：
- ✅ 中文字符
- ✅ 数学符号
- ✅ 希腊字母

**测试验证：**
```bash
cd /Users/enithz/Desktop/pdfnew
source venv/bin/activate
python test_font.py
# 查看生成的 test_font_output.pdf
```

---

## ☁️ Zeabur 部署（需要 3 步）

### 步骤 1：下载字体

访问 https://fonts.google.com/noto/specimen/Noto+Sans+SC

点击 "Download family" 按钮，下载字体文件。

### 步骤 2：放置字体

将下载的字体文件复制到项目：

```bash
# macOS/Linux
cp ~/Downloads/NotoSansSC-Regular.ttf /Users/enithz/Desktop/pdfnew/fonts/

# 提交到 Git
cd /Users/enithz/Desktop/pdfnew
git add fonts/NotoSansSC-Regular.ttf
git commit -m "添加 Noto Sans 字体"
git push
```

### 步骤 3：配置 Zeabur

在 Zeabur 控制台的环境变量中添加：

```
PDF_FONT_PATH=/app/fonts/NotoSansSC-Regular.ttf
```

---

## 📦 文件说明

| 文件 | 说明 |
|------|------|
| `Arial-Unicode.ttf` | 系统字体符号链接（本地开发用） |
| `README.md` | 详细配置说明 |
| `FONT_SETUP.md` | 完整配置指南 |
| `download_font.sh` | 自动下载脚本（可选） |
| `QUICK_START.md` | 本文件 |

---

## ❓ 常见问题

**Q: 为什么不直接包含字体文件？**  
A: Noto Sans CJK 字体约 16MB，由于网络问题无法自动下载，需要手动添加。

**Q: 本地开发需要下载字体吗？**  
A: 不需要，已配置使用系统字体。

**Q: PDF 显示黑色问号怎么办？**  
A: 说明字体未正确加载，检查：
1. 字体文件是否存在
2. 文件路径是否正确
3. 环境变量是否配置

**Q: 可以使用其他字体吗？**  
A: 可以，将字体文件放入 `fonts/` 目录，应用会自动尝试加载。

---

## 🎯 推荐工作流

### 开发阶段
使用当前配置（Arial Unicode），无需额外操作。

### 部署前
1. 手动下载 Noto Sans CJK SC
2. 测试验证：`python test_font.py`
3. 提交到 Git

### 部署后
1. 设置环境变量
2. 测试 PDF 生成
3. 检查中文和数学符号显示

---

## 📞 需要帮助？

详细配置和故障排除请查看：
- `README.md` - 完整说明
- `FONT_SETUP.md` - 详细指南
- `FONT_CONFIGURATION_SUMMARY.md` - 配置总结
