# GitHub Actions API 使用说明

本项目支持通过GitHub Actions执行YouTube搜索和评论获取功能，可以通过手动触发或HTTP请求触发。

## 🚀 功能特性

- ✅ **搜索模式**: 搜索YouTube视频并获取详细信息
- ✅ **评论模式**: 获取指定视频的热门评论
- ✅ **频道模式**: 根据频道ID获取频道所有视频信息
- ✅ **代理支持**: 支持HTTP/HTTPS/SOCKS代理访问
- ✅ **Webhook推送**: 支持将结果推送到飞书等平台
- ✅ **文件下载**: 结果自动保存为JSON文件

## 📋 前置准备

### 1. 设置GitHub Secrets

在GitHub仓库中设置以下Secret：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加以下Secret：

**必需的Secret：**
```
YOUTUBE_API_KEY: 你的YouTube Data API密钥
```

### 2. 获取GitHub Personal Access Token

1. 访问 GitHub → Settings → Developer settings → Personal access tokens
2. 生成新token，勾选 `repo` 权限
3. 保存token用于API调用

## 🎯 使用方法

### 方法1：手动触发（GitHub网页）

1. 访问仓库的Actions页面
2. 选择 "YouTube API (Search & Comments & Channel)" 工作流
3. 点击 "Run workflow"
4. 填写参数并运行

### 方法2：HTTP API触发

#### 触发评论获取

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "youtube-comments",
    "client_payload": {
      "mode": "comments",
      "video_id": "_xLryfjRJAc",
      "max_comments": "10",
      "webhook_url": "YOUR_WEBHOOK_URL"
    }
  }'
```

#### 触发视频搜索

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/dispatches \
  -d '{
    "event_type": "youtube-search",
    "client_payload": {
      "mode": "search",
      "search_query": "HONOR手机",
      "max_results": "25",
      "webhook_url": "YOUR_WEBHOOK_URL"
    }
  }'
```

#### 触发频道视频获取

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/k190513120/Google_search/dispatches \
  -d '{
    "event_type": "youtube-channel",
    "client_payload": {
      "mode": "channel",
      "channel_id": "UCBJycsmduvYEL83R_U4JriQ",
      "max_videos": "50",
      "webhook_url": "YOUR_WEBHOOK_URL"
    }
  }'
```

## 📊 参数说明

### 通用参数

| 参数 | 描述 | 必需 | 默认值 |
|------|------|------|--------|
| `mode` | 模式选择 (`search`、`comments` 或 `channel`) | 是 | `search` |
| `webhook_url` | Webhook推送地址 | 否 | - |

### 搜索模式参数

| 参数 | 描述 | 必需 | 默认值 |
|------|------|------|--------|
| `search_query` | 搜索关键词 | 是 | `HONOR 400` |
| `max_results` | 最大结果数量 | 否 | `25` |

### 评论模式参数

| 参数 | 描述 | 必需 | 默认值 |
|------|------|------|--------|
| `video_id` | YouTube视频ID | 是 | - |
| `max_comments` | 最大评论数量 | 否 | `50` |

### 频道模式参数

| 参数 | 描述 | 必需 | 默认值 |
|------|------|------|--------|
| `channel_id` | YouTube频道ID | 是 | - |
| `max_videos` | 最大视频数量 | 否 | `50` |



## 📄 结果获取

### 1. Webhook推送

如果设置了 `webhook_url`，结果会自动推送到指定地址。

### 2. 文件下载

如果未设置webhook，结果会保存为Artifacts：

1. 访问Actions页面
2. 点击对应的工作流运行记录
3. 在Artifacts部分下载结果文件

### 结果文件格式

**搜索结果**: `youtube_search_results_TIMESTAMP.json`
**评论结果**: `youtube_comments_VIDEOID_TIMESTAMP.json`
**频道结果**: `youtube_channel_CHANNELID_TIMESTAMP.json`

## 🔍 示例用法

### 获取视频评论（完整示例）

```bash
# 替换以下变量
GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
USERNAME="k190513120"
REPO="Google_search"
VIDEO_ID="_xLryfjRJAc"
WEBHOOK_URL="https://your-webhook-url.com"

# 发送请求
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$USERNAME/$REPO/dispatches \
  -d "{
    \"event_type\": \"youtube-comments\",
    \"client_payload\": {
      \"mode\": \"comments\",
      \"video_id\": \"$VIDEO_ID\",
      \"max_comments\": \"10\",
      \"webhook_url\": \"$WEBHOOK_URL\"
    }
  }"
```

### 获取频道视频（完整示例）

```bash
# 替换以下变量
GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
USERNAME="k190513120"
REPO="Google_search"
CHANNEL_ID="UCBJycsmduvYEL83R_U4JriQ"
WEBHOOK_URL="https://your-webhook-url.com"

# 发送请求
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$USERNAME/$REPO/dispatches \
  -d "{
    \"event_type\": \"youtube-channel\",
    \"client_payload\": {
      \"mode\": \"channel\",
      \"channel_id\": \"$CHANNEL_ID\",
      \"max_videos\": \"50\",
      \"webhook_url\": \"$WEBHOOK_URL\"
    }
  }"
```

### 本地测试（使用代理）

如果在中国大陆使用，需要配置代理避免timeout：

```bash
# 使用SOCKS代理（推荐）
SOCKS_PROXY="socks5://127.0.0.1:7890" python3 youtube_search_webhook.py channel UCsWXFpmDDCLzWmSaz2i-U6g 10 YOUR_API_KEY

# 使用HTTP代理
HTTP_PROXY="http://127.0.0.1:7890" python3 youtube_search_webhook.py channel UCsWXFpmDDCLzWmSaz2i-U6g 10 YOUR_API_KEY
```

## 🚨 注意事项

1. **API配额**: YouTube Data API有每日配额限制
2. **Token权限**: GitHub Token需要 `repo` 权限
3. **请求频率**: 避免过于频繁的API调用
4. **错误处理**: 查看Actions日志排查问题

## 🔧 故障排除

### 常见问题

1. **401 Unauthorized**: 检查GitHub Token权限
2. **API Key错误**: 检查YouTube API密钥设置
3. **网络超时**: 配置代理设置
4. **参数错误**: 检查请求参数格式

### 查看日志

1. 进入GitHub仓库 → Actions
2. 点击对应的工作流运行记录
3. 查看详细执行日志

---

📞 **技术支持**: 在仓库中创建Issue获取帮助