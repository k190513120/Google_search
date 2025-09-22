# GitHub Actions HTTP API 调用说明

## 概述

本项目支持通过HTTP API调用GitHub Actions来执行YouTube搜索、评论获取和频道视频获取任务。这允许您从外部系统、网站或应用程序触发这些操作。

## 前置准备

### 1. 获取GitHub Personal Access Token

1. 登录GitHub，进入 **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. 点击 **Generate new token (classic)**
3. 设置token名称和过期时间
4. 选择以下权限：
   - `repo` (完整仓库访问权限)
   - `workflow` (工作流权限)
5. 生成并保存token

### 2. 配置环境变量

```bash
export GITHUB_TOKEN="your_github_token_here"
```

## API端点

**基础URL**: `https://api.github.com/repos/{owner}/{repo}/dispatches`

- `{owner}`: GitHub用户名或组织名
- `{repo}`: 仓库名称

**示例**: `https://api.github.com/repos/k190513120/Google_search/dispatches`

## 请求格式

### 请求头

```json
{
  "Authorization": "token YOUR_GITHUB_TOKEN",
  "Accept": "application/vnd.github.v3+json",
  "Content-Type": "application/json"
}
```

### 请求体格式

```json
{
  "event_type": "事件类型",
  "client_payload": {
    "参数名": "参数值"
  }
}
```

## 支持的事件类型

### 1. YouTube搜索 (`youtube-search`)

**事件类型**: `youtube-search`

**参数**:
- `mode`: "search" (必需)
- `search_query`: 搜索关键词 (必需)
- `max_results`: 最大结果数量 (可选，默认25)
- `webhook_url`: Webhook URL (可选)
- `published_after`: 筛选时间范围：之后 (可选，格式: YYYY-MM-DD)
- `published_before`: 筛选时间范围：之前 (可选，格式: YYYY-MM-DD)

**示例请求**:
```json
{
  "event_type": "youtube-search",
  "client_payload": {
    "mode": "search",
    "search_query": "HONOR",
    "max_results": "10",
    "published_after": "2024-01-01",
    "published_before": "2024-12-31"
  }
}
```

### 2. YouTube评论获取 (`youtube-comments`)

**事件类型**: `youtube-comments`

**参数**:
- `mode`: "comments" (必需)
- `video_id`: YouTube视频ID (必需)
- `max_comments`: 最大评论数量 (可选，默认50)
- `webhook_url`: Webhook URL (可选)

**示例请求**:
```json
{
  "event_type": "youtube-comments",
  "client_payload": {
    "mode": "comments",
    "video_id": "dQw4w9WgXcQ",
    "max_comments": "20"
  }
}
```

### 3. YouTube频道视频获取 (`youtube-channel`)

**事件类型**: `youtube-channel`

**参数**:
- `mode`: "channel" (必需)
- `channel_handle`: 频道Handle (必需，如@JerryRigEverything)
- `max_videos`: 最大视频数量 (可选，默认50)
- `webhook_url`: Webhook URL (可选)

**示例请求**:
```json
{
  "event_type": "youtube-channel",
  "client_payload": {
    "mode": "channel",
    "channel_handle": "@JerryRigEverything",
    "max_videos": "15"
  }
}
```

## 使用示例

### cURL命令

```bash
# YouTube搜索示例
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "youtube-search",
    "client_payload": {
      "mode": "search",
      "search_query": "HONOR",
      "max_results": "10",
      "published_after": "2024-01-01"
    }
  }' \
  https://api.github.com/repos/k190513120/Google_search/dispatches
```

### Python示例

使用提供的 `trigger_action_example.py` 脚本：

```python
from trigger_action_example import GitHubActionTrigger

# 初始化
trigger = GitHubActionTrigger(
    github_token="your_token",
    repo_owner="k190513120",
    repo_name="Google_search"
)

# 触发搜索
trigger.trigger_youtube_search(
    search_query="HONOR",
    max_results=10,
    published_after="2024-01-01"
)
```

### JavaScript示例

```javascript
const triggerAction = async (eventType, payload) => {
  const response = await fetch('https://api.github.com/repos/k190513120/Google_search/dispatches', {
    method: 'POST',
    headers: {
      'Authorization': 'token YOUR_GITHUB_TOKEN',
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      event_type: eventType,
      client_payload: payload
    })
  });
  
  return response.status === 204;
};

// 使用示例
triggerAction('youtube-search', {
  mode: 'search',
  search_query: 'HONOR',
  max_results: '10',
  published_after: '2024-01-01'
});
```

## 响应说明

### 成功响应
- **状态码**: 204 No Content
- **说明**: Action已成功触发

### 错误响应
- **401 Unauthorized**: Token无效或权限不足
- **404 Not Found**: 仓库不存在或无访问权限
- **422 Unprocessable Entity**: 请求格式错误

## 监控执行状态

触发Action后，可以通过以下方式查看执行状态：

1. **GitHub网页**: `https://github.com/{owner}/{repo}/actions`
2. **GitHub API**: `https://api.github.com/repos/{owner}/{repo}/actions/runs`

## 注意事项

1. **Token安全**: 请妥善保管GitHub Token，不要在代码中硬编码
2. **频率限制**: GitHub API有频率限制，避免过于频繁的调用
3. **权限要求**: Token需要有仓库和工作流权限
4. **参数验证**: 确保传递的参数格式正确，特别是时间格式(YYYY-MM-DD)
5. **异步执行**: Action是异步执行的，需要通过GitHub界面或API查看结果

## 故障排除

### 常见问题

1. **401错误**: 检查Token是否正确，是否有足够权限
2. **404错误**: 检查仓库路径是否正确
3. **Action未触发**: 检查event_type是否匹配工作流配置
4. **参数错误**: 检查client_payload中的参数名称和格式

### 调试建议

1. 使用GitHub Actions页面查看详细日志
2. 检查工作流文件中的触发条件配置
3. 验证API请求格式是否正确
4. 确认所有必需参数都已提供