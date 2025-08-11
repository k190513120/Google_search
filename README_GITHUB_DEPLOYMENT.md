# YouTube搜索API - GitHub部署版本

这是一个基于GitHub Actions的YouTube视频搜索工具，可以通过webhook触发搜索并将结果发送到飞书多维表格等平台。

## 🚀 功能特性

- ✅ 通过YouTube Data API搜索视频
- ✅ 获取视频详细统计信息（观看数、点赞数等）
- ✅ 支持webhook结果推送（飞书多维表格等）
- ✅ GitHub Actions自动化执行
- ✅ 支持手动触发和外部webhook触发
- ✅ 结果文件自动保存和下载

## 📋 部署步骤

### 1. Fork或创建仓库

将此项目Fork到你的GitHub账户，或创建新仓库并上传代码文件。

### 2. 设置GitHub Secrets

在GitHub仓库中设置以下Secret：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下Secret：

```
YOUTUBE_API_KEY: 你的YouTube Data API密钥
```

#### 获取YouTube API密钥步骤：
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 "YouTube Data API v3"
4. 创建API密钥（凭据）
5. 复制API密钥到GitHub Secret

### 3. 文件结构

确保你的仓库包含以下文件：

```
.
├── .github/
│   └── workflows/
│       └── youtube-search.yml     # GitHub Actions工作流
├── youtube_search_webhook.py      # 主要搜索脚本
└── README_GITHUB_DEPLOYMENT.md    # 部署说明
```

## 🎯 使用方法

### 方法1：手动触发（推荐用于测试）

1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "YouTube Search API" 工作流
4. 点击 "Run workflow"
5. 填写参数：
   - **搜索关键词**：要搜索的内容（如："HONOR 400"）
   - **Webhook URL**：飞书多维表格webhook地址（可选）
   - **最大结果数量**：返回结果数量（默认25）

### 方法2：外部Webhook触发（推荐用于生产）

#### 设置GitHub Personal Access Token

1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新token，勾选 `repo` 权限
3. 保存token备用

#### 触发搜索请求

发送POST请求到GitHub API：

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "youtube-search",
    "client_payload": {
      "search_query": "HONOR 400",
      "webhook_url": "https://larkcommunity.feishu.cn/base/workflow/webhook/event/YOUR_WEBHOOK_ID",
      "max_results": "25"
    }
  }'
```

#### 参数说明：
- `YOUR_GITHUB_TOKEN`：你的GitHub Personal Access Token
- `YOUR_USERNAME`：你的GitHub用户名
- `YOUR_REPO`：仓库名称
- `search_query`：搜索关键词
- `webhook_url`：结果推送地址（可选）
- `max_results`：最大结果数量（可选，默认25）

## 📊 结果格式

搜索结果将以JSON格式发送到webhook，包含以下信息：

```json
{
  "basic_info": {
    "video_id": "视频ID",
    "title": "视频标题",
    "channel_title": "频道名称",
    "channel_id": "频道ID",
    "published_at": "发布时间",
    "video_url": "视频链接",
    "description": "视频描述"
  },
  "statistics": {
    "view_count": 观看次数,
    "like_count": 点赞数,
    "comment_count": 评论数,
    "favorite_count": 收藏数
  },
  "content_details": {
    "duration": "视频时长",
    "definition": "视频清晰度",
    "caption": "字幕信息"
  },
  "status": {
    "upload_status": "上传状态",
    "privacy_status": "隐私状态",
    "embeddable": "是否可嵌入"
  },
  "thumbnails": {
    "default": "默认缩略图",
    "medium": "中等缩略图",
    "high": "高清缩略图"
  },
  "search_metadata": {
    "search_query": "搜索关键词",
    "result_index": 结果序号,
    "timestamp": "搜索时间",
    "total_results": 总结果数
  }
}
```

## 🔧 配置选项

### 环境变量

- `YOUTUBE_API_KEY`：YouTube Data API密钥（必需）
- `SEARCH_QUERY`：搜索关键词（必需）
- `WEBHOOK_URL`：结果推送地址（可选）
- `MAX_RESULTS`：最大结果数量（可选，默认25）

### 工作流触发方式

1. **手动触发**：通过GitHub Actions界面手动运行
2. **Webhook触发**：通过GitHub API的repository_dispatch事件触发
3. **定时触发**：可以添加cron表达式实现定时搜索（需修改工作流文件）

## 📝 飞书多维表格集成

### 获取Webhook URL

1. 打开飞书多维表格
2. 点击右上角"自动化" → "创建自动化"
3. 选择"当接收到webhook请求时" → "添加记录"
4. 复制生成的Webhook URL
5. 在触发搜索时使用此URL

### 字段映射建议

在飞书多维表格中创建以下字段：

- 视频标题（单行文本）
- 频道名称（单行文本）
- 观看次数（数字）
- 点赞数（数字）
- 视频链接（URL）
- 发布时间（日期时间）
- 搜索关键词（单行文本）
- 搜索时间（日期时间）

## 🚨 注意事项

1. **API配额限制**：YouTube Data API有每日配额限制，请合理使用
2. **请求频率**：避免过于频繁的搜索请求
3. **数据准确性**：搜索结果基于YouTube API返回的数据
4. **隐私保护**：不要在代码中硬编码API密钥
5. **错误处理**：检查GitHub Actions日志以排查问题

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   - 检查GitHub Secret中的YOUTUBE_API_KEY是否正确
   - 确认API密钥有YouTube Data API v3权限

2. **搜索无结果**
   - 检查搜索关键词是否正确
   - 确认网络连接正常

3. **Webhook发送失败**
   - 检查webhook URL是否正确
   - 确认目标服务可以接收POST请求

4. **工作流无法触发**
   - 检查GitHub Token权限
   - 确认仓库名称和用户名正确

### 查看日志

1. 进入GitHub仓库 → Actions
2. 点击对应的工作流运行记录
3. 查看详细日志输出

## 📈 扩展功能

### 计划中的功能

- [ ] 评论数据采集（独立功能）
- [ ] 多关键词批量搜索
- [ ] 搜索结果去重
- [ ] 数据可视化报表
- [ ] 定时自动搜索
- [ ] 多平台webhook支持

### 自定义修改

你可以根据需要修改 `youtube_search_webhook.py` 文件：

- 调整搜索参数（排序方式、视频类型等）
- 修改数据格式
- 添加数据过滤逻辑
- 集成其他API服务

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

**快速开始**：
1. Fork仓库
2. 设置YOUTUBE_API_KEY Secret
3. 运行工作流测试
4. 集成到你的应用中

有问题？查看GitHub Issues或创建新的Issue！