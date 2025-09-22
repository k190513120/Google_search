# YouTube搜索API工具

这是一个功能强大的YouTube搜索工具，支持搜索视频、获取频道信息和评论数据，并提供了分页搜索功能来突破API的单次查询限制。

## ✨ 最新功能

### 🕒 时间筛选功能 (NEW!)
- 支持按发布时间范围筛选视频
- 可设置开始时间和结束时间
- 支持命令行、环境变量和GitHub Actions调用

### 🌐 HTTP API调用 (NEW!)
- 支持通过HTTP API远程触发GitHub Actions
- 无需本地环境，直接调用云端执行
- 支持所有功能模式（搜索、评论、频道）

## 🚀 主要功能

### 1. 视频搜索（支持分页）
- 🔍 **智能分页搜索**：自动突破YouTube API单次50条结果的限制
- 📊 **配额优化**：根据需求精确控制API调用次数，避免浪费
- 🎯 **灵活结果数**：支持获取任意数量的搜索结果（理论上无上限）
- 💰 **成本透明**：实时显示API配额消耗情况

### 2. 频道信息获取
- 📺 获取频道基本信息（名称、描述、订阅数等）
- 🌍 **新增**：频道国家信息支持
- 📹 批量获取频道所有视频
- 📊 详细的频道统计数据

### 3. 评论数据获取
- 💬 获取视频评论和回复
- 👥 评论者信息和互动数据
- 🔄 支持分页获取大量评论

## 📈 分页搜索功能详解

### 问题背景
YouTube Data API v3 的搜索接口单次最多只能返回50条结果，这对于需要大量数据的应用来说是一个限制。

### 解决方案
我们的分页搜索功能通过以下方式解决这个问题：

1. **自动分页**：使用 `nextPageToken` 自动获取后续页面
2. **智能批处理**：根据目标数量智能计算每次请求的结果数
3. **配额优化**：只请求需要的数量，避免过度消耗
4. **透明计费**：实时显示每次请求的配额消耗

### 配额消耗说明

| 结果数量 | 搜索请求次数 | 视频详情请求次数 | 总配额消耗 |
|---------|-------------|----------------|------------|
| 1-50    | 1次 (100配额) | 1次 (1配额)   | 101配额    |
| 51-100  | 2次 (200配额) | 2次 (2配额)   | 202配额    |
| 101-150 | 3次 (300配额) | 3次 (3配额)   | 303配额    |
| 151-200 | 4次 (400配额) | 4次 (4配额)   | 404配额    |

> **注意**：YouTube Data API v3 每日配额限制为 10,000 单位

## 🛠️ 安装和配置

### 1. 安装依赖
```bash
pip install google-api-python-client python-dotenv requests
```

### 2. 获取API密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用 YouTube Data API v3
4. 创建API密钥
5. 设置环境变量：
```bash
export YOUTUBE_API_KEY='your_api_key_here'
```

### 3. 代理配置（可选）
如果需要使用代理，可以设置以下环境变量：
```bash
export HTTP_PROXY='http://proxy_host:port'
export HTTPS_PROXY='https://proxy_host:port'
export SOCKS_PROXY='socks5://proxy_host:port'
```

## 📖 使用示例

### 基本搜索（25条结果）
```python
from youtube_search_webhook import search_youtube_videos

results = search_youtube_videos(
    api_key='your_api_key',
    search_query='Python编程教程',
    max_results=25
)
```

### 大量结果搜索（150条结果）
```python
results = search_youtube_videos(
    api_key='your_api_key',
    search_query='机器学习',
    max_results=150  # 将自动进行3次分页请求
)

print(f"获取到 {len(results)} 条结果")
```

### 频道信息获取
```python
from youtube_search_webhook import get_channel_videos

channel_info = get_channel_videos(
    api_key='your_api_key',
    channel_id='UC_channel_id_here',
    max_results=100
)
```

### 评论获取
```python
from youtube_search_webhook import get_video_comments

comments = get_video_comments(
    api_key='your_api_key',
    video_id='video_id_here',
    max_results=50
)
```

## 🧪 测试示例

运行分页搜索测试：
```bash
python example_pagination_search.py
```

这个示例会演示：
- 不同结果数量的配额消耗
- 分页搜索的实际效果
- 性能和成本分析

## 📊 返回数据结构

### 搜索结果
每个视频包含以下信息：
- **基本信息**：标题、描述、发布时间、频道信息
- **统计数据**：观看数、点赞数、评论数
- **技术参数**：时长、分辨率、隐私状态
- **缩略图**：多种尺寸的缩略图URL
- **分类信息**：视频分类、标签、语言

### 频道信息
- **基本信息**：频道名称、描述、创建时间
- **统计数据**：订阅数、视频总数、总观看数
- **地理信息**：频道国家（新增功能）
- **视频列表**：频道所有视频的详细信息

## ⚡ 性能优化建议

1. **合理设置结果数量**：根据实际需求设置 `max_results`，避免过度获取
2. **批量处理**：如果需要处理多个查询，建议批量进行以减少API调用频率
3. **缓存结果**：对于重复查询，建议实现本地缓存机制
4. **监控配额**：定期检查API配额使用情况，避免超限

## 🔧 高级功能

### Webhook支持
支持将结果发送到指定的webhook URL：
```python
results = search_youtube_videos(
    api_key='your_api_key',
    search_query='搜索关键词',
    max_results=100,
    webhook_url='https://your-webhook-url.com/endpoint'
)
```

### 命令行使用
```bash
# 搜索视频
python youtube_search_webhook.py search "搜索关键词" --max_results 100

# 获取频道信息
python youtube_search_webhook.py channel "频道ID" --max_results 50

# 获取评论
python youtube_search_webhook.py comments "视频ID" --max_results 30

# 使用时间筛选搜索视频 (NEW!)
python youtube_search_webhook.py search "搜索关键词" --max_results 100 --published_after "2024-01-01" --published_before "2024-12-31"
```

## 🕒 时间筛选功能使用指南

### 命令行参数
```bash
# 搜索2024年发布的视频
python youtube_search_webhook.py search "机器学习" --published_after "2024-01-01" --published_before "2024-12-31"

# 搜索最近30天的视频
python youtube_search_webhook.py search "Python教程" --published_after "2024-11-01"
```

### 环境变量设置
```bash
export PUBLISHED_AFTER="2024-01-01"
export PUBLISHED_BEFORE="2024-12-31"
python youtube_search_webhook.py search "搜索关键词"
```

### 支持的时间格式
- `YYYY-MM-DD`：如 `2024-01-01`
- `YYYY-MM-DD HH:MM:SS`：如 `2024-01-01 12:00:00`
- ISO 8601格式：如 `2024-01-01T12:00:00Z`

详细使用说明请参考：[TIME_FILTER_USAGE.md](TIME_FILTER_USAGE.md)

## 🌐 HTTP API调用

### 快速开始
1. 获取GitHub Personal Access Token
2. 配置环境变量：
   ```bash
   export GITHUB_TOKEN="your_github_token"
   export GITHUB_REPO="username/repository"
   ```

3. 使用Python脚本调用：
   ```python
   python trigger_action_example.py
   ```

### API端点
```
POST https://api.github.com/repos/{owner}/{repo}/dispatches
```

### 支持的事件类型
- `youtube-search`：视频搜索
- `youtube-comments`：评论获取  
- `youtube-channel`：频道视频获取

### 使用示例

#### cURL调用
```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/USERNAME/REPO/dispatches \
  -d '{
    "event_type": "youtube-search",
    "client_payload": {
      "search_query": "机器学习",
      "max_results": 50,
      "published_after": "2024-01-01",
      "published_before": "2024-12-31"
    }
  }'
```

#### Python调用
```python
import requests

def trigger_youtube_search(token, repo, query, max_results=50, published_after=None, published_before=None):
    url = f"https://api.github.com/repos/{repo}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "youtube-search",
        "client_payload": {
            "search_query": query,
            "max_results": max_results
        }
    }
    
    if published_after:
        payload["client_payload"]["published_after"] = published_after
    if published_before:
        payload["client_payload"]["published_before"] = published_before
    
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 204
```

详细API使用说明请参考：[HTTP_API_USAGE.md](HTTP_API_USAGE.md)

## 📝 更新日志

### v3.0.0 (最新)
- ✨ **新增**：时间筛选功能，支持按发布时间范围搜索视频
- ✨ **新增**：HTTP API调用支持，可远程触发GitHub Actions
- ✨ **新增**：命令行时间参数 `--published_after` 和 `--published_before`
- ✨ **新增**：环境变量时间配置支持
- 📚 **新增**：详细的使用文档和API调用示例
- 🔧 **优化**：GitHub Actions工作流支持更多触发方式

### v2.0.0
- ✨ **新增**：分页搜索功能，突破50条结果限制
- ✨ **新增**：频道国家信息支持
- 🔧 **优化**：API配额使用透明化
- 🔧 **优化**：批量处理视频详情获取
- 📊 **改进**：实时显示配额消耗情况

### v1.0.0
- 🎉 基础搜索功能
- 📺 频道信息获取
- 💬 评论数据获取
- 🌐 代理支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License

## 🔗 相关链接

- [YouTube Data API v3 文档](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API配额和限制](https://developers.google.com/youtube/v3/getting-started#quota)