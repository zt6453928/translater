# 🎨 前端界面更新说明

## ✨ 主要改进

### 1. **简洁现代的设计**
- 移除了所有不必要的图标和文字
- 采用扁平化、现代化的设计风格
- 清晰的视觉层次和间距

### 2. **全新配色方案**
- **主色调**: 科技蓝色 (#0ea5e9)
- **辅助色**: 青色 (#06b6d4)
- **渐变背景**: 蓝色渐变，营造AI科技感
- **移除紫色**: 采用更专业的蓝色系

### 3. **完全响应式**
- 完美适配桌面、平板和手机
- 移动端优化的触摸体验
- 自适应网格布局

### 4. **API管理功能**

#### 解析API管理
- 可添加多个解析API
- 配置项：
  - 名称（自定义）
  - API URL
  - API Token
- 本地存储，下次自动加载

#### 翻译AI API管理
- 可添加多个翻译AI API
- 支持OpenAI兼容接口
- 配置项：
  - 名称（自定义）
  - API URL (OpenAI兼容)
  - API Key
  - 模型名称
- 本地存储，下次自动加载

## 📱 界面变化对比

### 之前
```
标题: 📄 PDF翻译器
副标题: 支持英文PDF翻译成中文，保持原格式及图片

底部特性展示:
🔍 MinerU 2.5 解析
🌐 DeepLX 翻译
📝 保持原格式
🖼️ 支持图片

参数配置: ⚙️ MinerU 参数配置
```

### 现在
```
标题: 翻译 (简洁，渐变色)

无副标题
无底部特性展示

参数配置: 参数配置
- 解析配置
- API配置 (新增)
  - 解析API
  - 翻译AI API
```

## 🎯 使用方法

### 1. 上传文件
- 点击或拖拽PDF文件到上传区域
- 支持最大50MB

### 2. 配置参数（可选）
点击"参数配置"展开：

**解析配置**
- OCR识别：识别扫描版PDF
- 包含图片：提取图片内容
- 公式识别：识别数学公式
- 表格识别：识别表格结构
- 处理页数：指定处理范围
- 布局模型：选择布局识别模型

**API配置** (新功能)

*解析API*
1. 点击"添加"按钮
2. 输入配置信息：
   - 名称：如"主API"、"备用API"
   - API URL：解析服务地址
   - API Token：认证令牌
3. 可添加多个API作为备用

*翻译AI API*
1. 点击"添加"按钮
2. 输入配置信息：
   - 名称：如"Claude 4.5"
   - API URL：OpenAI兼容接口地址
   - API Key：如 sk-...
   - 模型名称：如 claude-4.5-sonnet-think
3. 可添加多个API供选择

### 3. 开始翻译
点击"开始翻译"按钮，系统会：
1. 上传文件
2. 使用配置的API进行解析
3. 使用配置的AI进行翻译
4. 自动下载生成的PDF

## 📐 设计规范

### 颜色
```css
主色：#0ea5e9 (蓝色)
主色深：#0284c7
主色浅：#38bdf8
辅助色：#06b6d4 (青色)
强调色：#8b5cf6 (紫色)
成功：#10b981
危险：#ef4444
警告：#f59e0b
```

### 间距
```css
xs: 0.25rem (4px)
sm: 0.5rem (8px)
md: 1rem (16px)
lg: 1.5rem (24px)
xl: 2rem (32px)
2xl: 3rem (48px)
```

### 圆角
```css
sm: 0.375rem
md: 0.5rem
lg: 0.75rem
xl: 1rem
2xl: 1.5rem
full: 9999px (完全圆形)
```

### 阴影
```css
sm: 细微阴影
md: 中等阴影
lg: 大阴影
xl: 超大阴影
```

## 📱 响应式断点

```css
手机: < 480px
  - 单列布局
  - 大按钮
  - 简化导航

平板: 480px - 768px
  - 两列网格
  - 中等间距

桌面: > 768px
  - 多列网格
  - 完整功能
```

## 🎨 图标系统

使用Heroicons的SVG图标：
- 上传：cloud-upload
- 文件：document
- 删除：trash
- 添加：plus
- 成功：check-circle
- 下拉：chevron-down

所有图标都是内联SVG，无需外部依赖。

## 🔧 技术细节

### HTML结构
```html
container
  ├── header (标题)
  ├── main
  │   ├── upload-section (上传)
  │   ├── config-section (配置)
  │   │   ├── config-group (解析配置)
  │   │   └── config-group (API配置)
  │   ├── action-section (翻译按钮)
  │   ├── progress-section (进度)
  │   └── result-section (结果)
```

### CSS特性
- CSS变量 (var())
- Flexbox & Grid布局
- CSS过渡和动画
- 媒体查询
- 现代渐变

### JavaScript功能
- localStorage API管理
- FormData文件上传
- Fetch API请求
- 动态DOM操作
- 事件处理

## 💾 数据存储

API配置保存在浏览器localStorage中：
```javascript
localStorage.getItem('parseAPIs')    // 解析API列表
localStorage.getItem('translateAPIs') // 翻译API列表
```

数据格式：
```json
{
  "id": 1639123456789,
  "name": "我的API",
  "url": "https://api.example.com",
  "apiKey": "sk-...",
  "model": "claude-4.5-sonnet-think"
}
```

## 🚀 性能优化

1. **最小化重绘**
   - CSS过渡替代JavaScript动画
   - 合理使用transform

2. **懒加载**
   - 配置区域默认折叠
   - 按需渲染API列表

3. **缓存**
   - localStorage缓存API配置
   - 避免重复输入

4. **响应式图片**
   - SVG图标，矢量缩放
   - 无需多种尺寸

## 🔐 安全考虑

1. **API密钥**
   - 存储在localStorage (仅客户端)
   - 使用type="password"输入框
   - 建议使用HTTPS

2. **文件验证**
   - 客户端文件类型检查
   - 文件大小限制
   - 服务端二次验证

## 📝 维护建议

### 添加新功能
1. 更新HTML结构
2. 添加对应CSS样式
3. 实现JavaScript逻辑
4. 更新此文档

### 修改样式
1. 优先修改CSS变量
2. 保持响应式兼容
3. 测试多种设备

### 调试
- 使用浏览器开发者工具
- 检查控制台日志
- 测试localStorage存储

## 🎯 未来改进建议

1. **Toast通知**
   - 替换alert弹窗
   - 更优雅的消息提示

2. **API测试**
   - 添加"测试连接"按钮
   - 验证API配置正确性

3. **主题切换**
   - 浅色/深色模式
   - 用户偏好保存

4. **批量处理**
   - 支持多文件上传
   - 队列管理

5. **历史记录**
   - 保存翻译历史
   - 快速重新下载

6. **国际化**
   - 多语言支持
   - i18n实现

## 🐛 已知问题

无

## 📞 反馈

如有问题或建议，请及时反馈。

---

**更新时间**: 2025-12-11
**版本**: 2.0.0
