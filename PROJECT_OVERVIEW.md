# 项目概览

## 🎯 项目简介

**PDF翻译器** 是一个基于Web的PDF文档翻译工具，专注于将英文PDF翻译成中文，同时保持原文档格式和图片。

## 🏗️ 技术架构

### 核心技术栈

**后端框架**
- Flask 3.0.0 - Python Web框架
- Python 3.7+ 

**API集成**
- MinerU 2.5 API - 文档解析和内容提取
- DeepLX API - 文本翻译服务

**关键库**
- requests - HTTP请求处理
- requests-toolbelt - 多部分表单数据编码
- reportlab - PDF生成
- markdown - Markdown内容处理

**前端**
- 原生HTML5/CSS3/JavaScript
- 响应式设计
- 现代化UI/UX

## 📊 工作流程

```
用户上传PDF
    ↓
保存到服务器临时目录
    ↓
调用MinerU API解析PDF
    ↓
获取Markdown格式内容
    ↓
逐行/逐段翻译文本（DeepLX API）
    ↓
使用ReportLab生成新PDF
    ↓
返回给用户下载
    ↓
清理临时文件
```

## 📁 项目结构

```
pdfnew/
│
├── app.py                  # Flask主应用，核心业务逻辑
├── config.py               # 配置文件，API和参数配置
├── requirements.txt        # Python依赖列表
├── run.sh                  # 一键启动脚本
├── .gitignore             # Git忽略文件
│
├── templates/             # Flask模板目录
│   └── index.html        # 主页面HTML
│
├── static/               # 静态资源目录
│   ├── css/
│   │   └── style.css    # 样式表
│   └── js/
│       └── main.js      # 前端交互脚本
│
└── 文档/
    ├── README.md         # 项目完整文档
    ├── QUICKSTART.md     # 快速开始指南
    ├── USAGE.md          # 详细使用指南
    └── PROJECT_OVERVIEW.md  # 本文档
```

## 🔧 核心功能模块

### 1. PDF解析模块 (`parse_pdf_with_mineru`)
- 上传PDF到MinerU API
- 配置解析参数（OCR、图片、公式、表格）
- 获取解析任务ID

### 2. 任务轮询模块 (`poll_mineru_task`)
- 定期检查任务状态
- 超时控制
- 错误处理

### 3. 翻译模块 (`translate_with_deeplx`)
- 调用DeepLX API
- 英译中翻译
- 错误重试机制

### 4. Markdown翻译模块 (`translate_markdown_content`)
- 保留Markdown格式
- 跳过代码块和图片
- 逐行智能翻译

### 5. PDF生成模块 (`markdown_to_pdf`)
- 中文字体支持
- 格式化处理
- 样式应用

### 6. Web路由
- `/` - 主页面
- `/translate` - 翻译API端点

## 🔌 API集成详情

### MinerU 2.5 API

**端点**: `https://ai.gitee.com/v1/async/documents/parse`

**功能**:
- 异步文档解析
- OCR文本识别
- 图片Base64提取
- 公式识别
- 表格结构化
- 布局分析

**参数**:
```python
{
    "model": "MinerU2.5",
    "is_ocr": True,
    "include_image_base64": True,
    "formula_enable": True,
    "table_enable": True,
    "layout_model": "doclayout_yolo",
    "output_format": "md"
}
```

### DeepLX API

**端点**: 配置的DeepLX URL

**功能**:
- 文本翻译
- 多语言支持
- 高质量翻译

**参数**:
```python
{
    "text": "要翻译的文本",
    "source_lang": "EN",
    "target_lang": "ZH"
}
```

## 🎨 前端设计

### UI特点
- 渐变色背景（紫色主题）
- 卡片式布局
- 拖拽上传支持
- 实时进度显示
- 动画效果

### 用户交互
1. 文件上传（点击/拖拽）
2. 文件信息展示
3. 翻译进度条
4. 成功提示
5. 自动下载

## 🔒 安全特性

- 文件大小限制（50MB）
- 文件类型验证
- 临时文件自动清理
- API Token保护
- 错误处理机制

## ⚡ 性能优化

- 异步任务处理
- 智能轮询间隔
- 翻译速率控制
- 临时文件管理
- 响应缓存

## 🧪 测试建议

### 单元测试
- API调用测试
- 文件处理测试
- 翻译逻辑测试

### 集成测试
- 完整流程测试
- 错误场景测试
- 超时测试

### 性能测试
- 大文件处理
- 并发请求
- 内存使用

## 📈 扩展方向

### 短期目标
- [ ] 添加用户认证
- [ ] 翻译历史记录
- [ ] 批量文件处理
- [ ] 进度持久化

### 中期目标
- [ ] 多语言对支持
- [ ] 自定义翻译引擎
- [ ] PDF编辑功能
- [ ] 云端存储集成

### 长期目标
- [ ] 机器学习优化
- [ ] 分布式处理
- [ ] 移动应用
- [ ] API服务化

## 🐛 已知限制

1. **文件大小**: 最大50MB
2. **语言支持**: 仅英译中
3. **格式保持**: 复杂PDF可能有偏差
4. **处理时间**: 大文件需要较长时间
5. **API限制**: 受服务商限制

## 💡 开发规范

### 代码风格
- PEP 8 Python代码规范
- 清晰的函数命名
- 详细的注释
- 错误处理

### Git提交
- 有意义的提交信息
- 小步提交
- 功能分支开发

### 文档
- README维护
- API文档更新
- 注释完整

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 编写测试
5. 发起Pull Request

## 📞 技术支持

- 查看文档目录下的各类指南
- GitHub Issues反馈问题
- 代码中的详细注释

## 📊 项目统计

- **代码行数**: 约800行（Python + HTML + CSS + JS）
- **文件数量**: 12个核心文件
- **依赖包**: 6个Python包
- **文档页数**: 4个完整文档

## 🎓 学习价值

通过这个项目，你可以学习：
- Flask Web开发
- API集成
- 文件处理
- PDF操作
- 前端交互
- 异步任务处理

---

**项目完成时间**: 2025-12-10
**开发环境**: macOS
**Python版本**: 3.7+












