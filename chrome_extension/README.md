# 飞书多维表格浏览器插件

一个Chrome浏览器插件，用于快速创建飞书多维表格并写入数据。

## 功能特性

- 🔧 **配置管理**：安全存储APP_TOKEN和PERSONAL_BASE_TOKEN
- 📊 **表格创建**：支持多种字段类型的表格创建
- ✍️ **数据写入**：支持表单模式和JSON模式的数据输入
- 🔍 **状态监控**：实时显示操作状态和结果反馈

## 安装使用

### 开发环境

1. 安装依赖：
```bash
npm install
```

2. 构建项目：
```bash
npm run build
```

3. 在Chrome中加载扩展：
   - 打开Chrome扩展管理页面 `chrome://extensions/`
   - 开启"开发者模式"
   - 点击"加载已解压的扩展程序"
   - 选择项目的`dist`目录

### 使用步骤

1. **配置认证信息**
   - 点击插件图标打开弹窗
   - 在配置页面输入APP_TOKEN和PERSONAL_BASE_TOKEN
   - 点击"测试连接"确保配置正确
   - 保存配置

2. **创建表格**
   - 切换到"创建表格"标签
   - 输入表格名称
   - 配置字段信息（名称和类型）
   - 点击"创建表格"按钮

3. **写入数据**
   - 表格创建成功后自动切换到"写入数据"标签
   - 选择表单模式或JSON模式
   - 填写数据内容
   - 点击"写入数据"按钮

## 技术架构

- **前端框架**：React + TypeScript
- **构建工具**：Vite
- **API集成**：飞书开放平台API
- **存储方案**：Chrome Storage API

## 项目结构

```
├── manifest.json          # Chrome扩展配置
├── popup.html             # 弹窗页面
├── src/
│   ├── App.tsx            # 主应用组件
│   ├── popup.tsx          # 弹窗入口
│   ├── background.ts      # 后台脚本
│   ├── content.ts         # 内容脚本
│   └── components/        # React组件
│       ├── ConfigPanel.tsx    # 配置面板
│       ├── TableCreator.tsx   # 表格创建
│       ├── DataWriter.tsx     # 数据写入
│       └── StatusDisplay.tsx  # 状态显示
└── public/
    └── icons/             # 插件图标
```

## 开发说明

### 获取认证信息

1. **APP_TOKEN**：从飞书多维表格URL中获取
   - URL格式：`https://xxx.feishu.cn/base/{APP_TOKEN}`
   - 或使用飞书开发工具插件获取

2. **PERSONAL_BASE_TOKEN**：在表格设置中生成
   - 打开表格设置
   - 找到"高级设置" > "开发者选项"
   - 生成个人访问令牌

### 支持的字段类型

- 文本 (Text)
- 数字 (Number)
- 单选 (SingleSelect)
- 多选 (MultiSelect)
- 日期时间 (DateTime)
- 复选框 (Checkbox)
- 人员 (User)
- 电话号码 (Phone)
- 超链接 (Url)
- 附件 (Attachment)
- 评分 (Rating)
- 进度 (Progress)

## 注意事项

- 使用PERSONAL_BASE_TOKEN访问OpenAPI有频率限制（单文档2qps）
- 确保网络连接正常，能够访问飞书开放平台API
- 建议在测试环境中先验证功能再在生产环境使用

## 许可证

MIT License