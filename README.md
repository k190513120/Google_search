# YouTube搜索API工具

这是一个功能强大的YouTube搜索工具，支持搜索视频、获取频道信息和评论数据，并提供了分页搜索功能来突破API的单次查询限制。

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
```

## 📝 更新日志

### v2.0.0 (最新)
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