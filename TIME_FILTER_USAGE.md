# YouTube视频搜索时间筛选功能使用说明

## 功能概述

YouTube视频搜索现已支持按发布时间筛选视频，可以指定搜索特定时间范围内发布的视频。

## 使用方法

### 1. 命令行使用

```bash
python3 youtube_search_webhook.py search "关键词" 结果数量 API密钥 webhook_url 开始时间 结束时间
```

**参数说明：**
- `开始时间` (published_after): 筛选此时间之后发布的视频，格式：YYYY-MM-DD
- `结束时间` (published_before): 筛选此时间之前发布的视频，格式：YYYY-MM-DD

**示例：**
```bash
# 搜索2024年1月1日之后发布的HONOR相关视频
python3 youtube_search_webhook.py search "HONOR" 10 "YOUR_API_KEY" "" "2024-01-01"

# 搜索2024年1月1日到2024年6月30日之间发布的视频
python3 youtube_search_webhook.py search "HONOR" 10 "YOUR_API_KEY" "" "2024-01-01" "2024-06-30"

# 搜索2024年6月30日之前发布的视频
python3 youtube_search_webhook.py search "HONOR" 10 "YOUR_API_KEY" "" "" "2024-06-30"
```

### 2. 环境变量使用

设置环境变量：
```bash
export PUBLISHED_AFTER="2024-01-01"
export PUBLISHED_BEFORE="2024-12-31"
```

然后运行搜索：
```bash
python3 youtube_search_webhook.py search "HONOR" 10 "YOUR_API_KEY"
```

### 3. GitHub Actions使用

在GitHub Actions工作流中，可以通过输入参数设置时间筛选：

```yaml
- name: 运行YouTube搜索
  uses: ./.github/workflows/youtube-search.yml
  with:
    mode: 'search'
    search_query: 'HONOR'
    max_results: '10'
    published_after: '2024-01-01'
    published_before: '2024-12-31'
```

## 时间格式说明

- **输入格式**: YYYY-MM-DD (例如: 2024-01-01)
- **API格式**: 系统会自动转换为YouTube API要求的RFC 3339格式
  - `published_after`: 2024-01-01 → 2024-01-01T00:00:00Z
  - `published_before`: 2024-12-31 → 2024-12-31T23:59:59Z

## 注意事项

1. **时间参数可选**: 可以只设置开始时间或结束时间，也可以同时设置
2. **时间范围**: YouTube API对时间范围有一定限制，建议不要设置过于久远的时间
3. **格式要求**: 时间格式必须为YYYY-MM-DD，其他格式可能导致搜索失败
4. **参数顺序**: 在命令行中，时间参数位于最后两个位置

## 功能验证

可以运行测试脚本验证时间筛选逻辑：
```bash
python3 test_time_filter.py
```

该脚本会验证时间参数的处理逻辑和格式转换是否正确。