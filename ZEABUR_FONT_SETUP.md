# Zeabur 字体配置说明

## ⚠️ 重要提示

**符号链接在容器中不工作！**

`fonts/Arial-Unicode.ttf` 是一个符号链接，指向本地 macOS 系统字体。这在本地开发环境中有效，但在 Zeabur 容器中无效，因为容器内没有 macOS 系统字体。

---

## 🐛 症状

如果您看到以下日志：

```
自定义字体路径: /app/fonts/Arial-Unicode.ttf
✓ 使用内置CID字体: STSong-Light
```

这说明：
1. ✅ 环境变量设置正确
2. ❌ 但字体文件加载失败（符号链接目标不存在）
3. ⚠️ 回退到内置 CID 字体

---

## ✅ 正确的解决方案

### 必须使用真实的字体文件

您需要下载并提交**真实的字体文件**，而不是符号链接。

---

## 📥 下载字体

### 方法 1：Google Fonts（推荐）

1. **访问下载页面**：
   ```
   https://fonts.google.com/noto/specimen/Noto+Sans+SC
   ```

2. **点击下载按钮**：
   - 右上角 "Download family"

3. **解压并复制**：
   ```bash
   # 解压下载的 ZIP 文件
   unzip ~/Downloads/Noto_Sans_SC.zip -d ~/Downloads/Noto_Sans_SC/
   
   # 复制字体到项目
   cp ~/Downloads/Noto_Sans_SC/NotoSansSC-Regular.ttf \
      /Users/enithz/Desktop/pdfnew/fonts/
   ```

### 方法 2：GitHub Releases（备选）

1. **访问发布页面**：
   ```
   https://github.com/googlefonts/noto-cjk/releases
   ```

2. **下载 Sans.zip**

3. **解压并复制**：
   ```bash
   unzip ~/Downloads/Sans.zip -d ~/Downloads/Sans/
   
   cp ~/Downloads/Sans/SimplifiedChinese/NotoSansCJKsc-Regular.otf \
      /Users/enithz/Desktop/pdfnew/fonts/
   ```

---

## 🔄 提交到 Git

下载完成后，提交字体文件：

```bash
cd /Users/enithz/Desktop/pdfnew

# 添加字体文件
git add fonts/NotoSans*.ttf fonts/NotoSans*.otf

# 查看文件大小
ls -lh fonts/Noto*

# 提交
git commit -m "添加 Noto Sans 字体文件用于 Zeabur 部署"

# 推送
git push origin master
```

---

## ⚙️ 更新 Zeabur 环境变量

根据您下载的字体文件，在 Zeabur 控制台设置：

### 如果下载的是 Google Fonts 版本：
```
PDF_FONT_PATH=/app/fonts/NotoSansSC-Regular.ttf
```

### 如果下载的是 GitHub 版本：
```
PDF_FONT_PATH=/app/fonts/NotoSansCJKsc-Regular.otf
```

---

## ✅ 验证部署

部署完成后，查看日志应该显示：

```
自定义字体路径: /app/fonts/NotoSansSC-Regular.ttf
✓ 成功注册字体: NotoSansSC-Regular.ttf
✓ 字体文件大小: 16.xx MB
```

而**不是**：
```
✓ 使用内置CID字体: STSong-Light
```

---

## 📊 字体文件大小参考

| 字体文件 | 大小 | 说明 |
|---------|------|------|
| `NotoSansSC-Regular.ttf` | ~5-8 MB | Google Fonts 版本 |
| `NotoSansCJKsc-Regular.otf` | ~16 MB | 完整版本（推荐） |
| `Arial-Unicode.ttf` (符号链接) | 0 字节 | ⚠️ 容器中不可用 |

---

## ❓ 常见问题

### Q: 为什么本地开发可以，Zeabur 不行？

**A:** 因为本地有 macOS 系统字体，符号链接可以解析。Zeabur 容器是 Linux 环境，没有 macOS 字体。

### Q: 可以删除 Arial-Unicode.ttf 符号链接吗？

**A:** 可以，但不建议。它对本地开发有用。添加真实字体文件后，应用会优先使用真实文件。

### Q: 字体文件太大怎么办？

**A:** 
1. Noto Sans SC 完整版约 16MB，这是必要的
2. 如果担心仓库大小，可以使用 Dockerfile 方案（在构建时下载）
3. 或者使用 .gitattributes 配置 Git LFS

### Q: 为什么不能自动下载字体？

**A:** 之前尝试过，但遇到网络 SSL 连接问题，无法稳定下载。手动下载更可靠。

---

## 🔧 替代方案：Dockerfile

如果不想提交字体文件到 Git，可以使用 Dockerfile：

```dockerfile
FROM python:3.11-slim

# 安装中文字体
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# 设置字体环境变量
ENV PDF_FONT_PATH=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc

EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

然后更新 `zeabur.json`：

```json
{
  "build": {
    "dockerfile": "Dockerfile"
  },
  "deploy": {
    "port": 8000,
    "healthCheckPath": "/health"
  }
}
```

---

## 📝 总结

| 环境 | 字体来源 | 状态 |
|------|---------|------|
| **本地开发** | Arial-Unicode.ttf (符号链接) | ✅ 可用 |
| **Zeabur 容器** | 需要真实字体文件 | ⚠️ 必须下载 |

**关键点：容器中必须使用真实的字体文件，符号链接不起作用！**

---

## 🆘 需要帮助？

如果下载字体遇到问题，或有其他疑问，请查看：
- `fonts/QUICK_START.md` - 快速开始
- `fonts/FONT_SETUP.md` - 详细配置
- `FONT_CONFIGURATION_SUMMARY.md` - 技术总结
