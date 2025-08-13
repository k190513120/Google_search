# YouTube频道视频获取功能使用示例

本文档展示如何使用新增的频道模式功能获取YouTube频道的视频信息。

## 🎯 功能特性

### 📊 获取的频道信息
- 频道ID、名称、描述
- 自定义URL、发布时间
- 订阅者数、视频总数、总观看数
- 频道缩略图URL

### 🎬 获取的视频字段（已增强）

#### 基础信息
- `video_id`: 视频ID
- `title`: 视频标题
- `description`: 视频描述
- `published_at`: 发布时间
- `video_url`: 视频链接

#### 统计数据
- `view_count`: 观看次数
- `like_count`: 点赞数
- `comment_count`: 评论数

#### 内容详情
- `duration`: 视频时长
- `definition`: 视频清晰度 (hd/sd)
- `caption`: 是否有字幕
- `dimension`: 视频维度 (2d/3d)
- `projection`: 投影类型 (rectangular/360)
- `has_custom_thumbnail`: 是否有自定义缩略图

#### 缩略图信息
- `thumbnails`: 完整缩略图对象
  - `default`: 120x90
  - `medium`: 320x180
  - `high`: 480x360
  - `standard`: 640x480
  - `maxres`: 1280x720

#### 状态信息
- `privacy_status`: 隐私状态
- `upload_status`: 上传状态
- `license`: 许可证类型
- `embeddable`: 是否可嵌入
- `public_stats_viewable`: 统计数据是否公开
- `made_for_kids`: 是否为儿童内容

#### 语言和分类
- `default_language`: 默认语言
- `default_audio_language`: 音频语言
- `category_id`: 分类ID
- `tags`: 标签列表
- `live_broadcast_content`: 直播状态

#### 录制详情（可选）
- `recording_date`: 录制日期
- `location_description`: 录制地点描述
- `location`: 地理位置信息

#### 主题分类（可选）
- `topic_ids`: 主题ID列表
- `topic_categories`: 主题分类URL列表

## 🚀 使用方法

### 方法1：命令行直接调用

```bash
# 基本用法
python3 youtube_search_webhook.py channel CHANNEL_ID MAX_VIDEOS API_KEY

# 实际示例
python3 youtube_search_webhook.py channel UCsWXFpmDDCLzWmSaz2i-U6g 20 YOUR_API_KEY

# 使用代理（推荐在中国大陆使用）
SOCKS_PROXY="socks5://127.0.0.1:7890" python3 youtube_search_webhook.py channel UCsWXFpmDDCLzWmSaz2i-U6g 20 YOUR_API_KEY
```

### 方法2：通过GitHub API触发

```bash
# 设置变量
GITHUB_TOKEN="your_github_token"
USERNAME="your_username"
REPO="your_repo_name"
CHANNEL_ID="UCsWXFpmDDCLzWmSaz2i-U6g"
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

## 📋 返回数据示例

```json
{
  "channel_info": {
    "channel_id": "UCsWXFpmDDCLzWmSaz2i-U6g",
    "title": "Hemel 360°",
    "description": "频道描述...",
    "custom_url": "@hemel360",
    "published_at": "2021-08-09T18:17:10.629331Z",
    "subscriber_count": 209000,
    "video_count": 5522,
    "view_count": 155034070,
    "channel_url": "https://www.youtube.com/channel/UCsWXFpmDDCLzWmSaz2i-U6g"
  },
  "videos": [
    {
      "video_id": "H1aqWHwZpkc",
      "title": "视频标题",
      "description": "视频描述",
      "published_at": "2025-08-13T07:50:00Z",
      "duration": "PT8S",
      "view_count": 8137,
      "like_count": 112,
      "comment_count": 6,
      "privacy_status": "public",
      "video_url": "https://www.youtube.com/watch?v=H1aqWHwZpkc",
      "thumbnails": {
        "default": {
          "url": "https://i.ytimg.com/vi/H1aqWHwZpkc/default.jpg",
          "width": 120,
          "height": 90
        },
        "maxres": {
          "url": "https://i.ytimg.com/vi/H1aqWHwZpkc/maxresdefault.jpg",
          "width": 1280,
          "height": 720
        }
      },
      "live_broadcast_content": "none",
      "default_audio_language": "bn",
      "dimension": "2d",
      "projection": "rectangular",
      "upload_status": "processed",
      "license": "youtube",
      "embeddable": true,
      "made_for_kids": false,
      "topic_categories": [
        "https://en.wikipedia.org/wiki/Technology"
      ]
    }
  ],
  "total_videos_fetched": 5,
  "fetch_timestamp": "2025-01-14T12:30:45.123456"
}
```

## 🌐 代理配置

**重要：GitHub Actions环境会自动检测并跳过代理配置，无需手动设置。**

如果在本地环境（中国大陆）使用，建议配置代理避免超时：

### SOCKS代理（推荐）
```bash
SOCKS_PROXY="socks5://127.0.0.1:7890" python3 youtube_search_webhook.py channel CHANNEL_ID 10 API_KEY
```

### HTTP代理
```bash
HTTP_PROXY="http://127.0.0.1:7890" python3 youtube_search_webhook.py channel CHANNEL_ID 10 API_KEY
```

### 环境变量设置
```bash
export SOCKS_PROXY="socks5://127.0.0.1:7890"
python3 youtube_search_webhook.py channel CHANNEL_ID 10 API_KEY
```

### 环境自动检测
- **GitHub Actions环境**：自动直连YouTube API，无需代理配置
- **本地环境**：根据环境变量（SOCKS_PROXY、HTTP_PROXY、HTTPS_PROXY）自动配置代理

## 📝 注意事项

1. **API配额**: 频道模式会消耗更多API配额，建议合理设置`max_videos`参数
2. **代理配置**: 在网络受限地区使用时，务必配置代理
3. **字段可用性**: 某些字段（如录制详情、主题分类）可能为空
4. **排序方式**: 返回的视频按观看数降序排列
5. **文件保存**: 结果会自动保存为JSON文件，格式：`youtube_channel_CHANNELID_TIMESTAMP.json`

## 🔗 相关文档

- [GitHub API使用说明](./GITHUB_API_USAGE.md)
- [YouTube API字段说明](./YOUTUBE_API_FIELDS.md)
- [代理设置指南](./PROXY_SETUP.md)