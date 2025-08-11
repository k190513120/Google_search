# YouTube Data API v3 完整字段说明

本文档详细说明了 `youtube_search_webhook.py` 脚本从 YouTube Data API v3 获取的所有字段信息。

## 📋 字段结构概览

### 1. basic_info (基本信息)
- `kind`: 资源类型标识符
- `etag`: 实体标签，用于缓存验证
- `video_id`: YouTube视频唯一标识符
- `video_url`: 视频完整URL链接

### 2. snippet (视频片段信息)
- `published_at`: 视频发布时间 (ISO 8601格式)
- `channel_id`: 频道唯一标识符
- `title`: 视频标题
- `description`: 视频描述
- `channel_title`: 频道名称
- `tags`: 视频标签数组
- `category_id`: 视频分类ID
- `live_broadcast_content`: 直播内容状态 (none/upcoming/live)
- `default_language`: 视频默认语言
- `default_audio_language`: 音频默认语言
- `localized`: 本地化信息对象
- `publish_time`: 发布时间 (详细版本)

### 3. statistics (统计数据)
- `view_count`: 观看次数
- `like_count`: 点赞数
- `dislike_count`: 踩数 (已弃用，通常为0)
- `comment_count`: 评论数
- `favorite_count`: 收藏数

### 4. content_details (内容详情)
- `duration`: 视频时长 (ISO 8601 duration格式)
- `dimension`: 视频维度 (2d/3d)
- `definition`: 视频清晰度 (hd/sd)
- `caption`: 字幕可用性 (true/false)
- `licensed_content`: 是否为许可内容
- `region_restriction`: 地区限制信息
  - `allowed`: 允许观看的国家/地区列表
  - `blocked`: 禁止观看的国家/地区列表
- `content_rating`: 内容分级信息
- `projection`: 视频投影类型 (rectangular/360)
- `has_custom_thumbnail`: 是否有自定义缩略图

### 5. status (状态信息)
- `upload_status`: 上传状态 (uploaded/processed/failed/rejected/deleted)
- `failure_reason`: 失败原因
- `rejection_reason`: 拒绝原因
- `privacy_status`: 隐私状态 (public/unlisted/private)
- `publish_at`: 计划发布时间
- `license`: 许可证类型 (youtube/creativeCommon)
- `embeddable`: 是否可嵌入
- `public_stats_viewable`: 统计数据是否公开可见
- `made_for_kids`: 是否为儿童内容
- `self_declared_made_for_kids`: 创作者是否自声明为儿童内容

### 6. thumbnails (缩略图)
- `default`: 默认缩略图 (120x90)
- `medium`: 中等缩略图 (320x180)
- `high`: 高清缩略图 (480x360)
- `standard`: 标准缩略图 (640x480)
- `maxres`: 最高分辨率缩略图 (1280x720)

每个缩略图对象包含：
- `url`: 图片URL
- `width`: 图片宽度
- `height`: 图片高度

### 7. recording_details (录制详情)
- `location_description`: 录制地点描述
- `location`: 录制地理位置
  - `latitude`: 纬度
  - `longitude`: 经度
  - `altitude`: 海拔
- `recording_date`: 录制日期

### 8. topic_details (主题详情)
- `topic_ids`: 主题ID列表
- `relevant_topic_ids`: 相关主题ID列表
- `topic_categories`: 主题分类URL列表

### 9. search_metadata (搜索元数据)
- `search_query`: 搜索查询词
- `result_index`: 结果索引位置
- `timestamp`: 数据获取时间戳
- `total_results`: 总结果数
- `search_kind`: 搜索结果类型

## 🔍 API部分说明

脚本使用以下API部分获取完整数据：

1. **search().list()** - 获取搜索结果基本信息
   - `part="snippet"`

2. **videos().list()** - 获取视频详细信息
   - `part="snippet,statistics,contentDetails,status,recordingDetails,topicDetails"`

## 📊 配额消耗

- 搜索请求: 100 单位/请求
- 视频详情请求: 1 单位/视频 × 部分数量
  - snippet: 2 单位
  - statistics: 2 单位
  - contentDetails: 2 单位
  - status: 2 单位
  - recordingDetails: 2 单位
  - topicDetails: 2 单位
  - 总计: 12 单位/视频

## 🚨 注意事项

1. **dislike_count**: YouTube已停止提供踩数据，该字段通常返回0或不存在
2. **recordingDetails**: 只有部分视频包含录制详情
3. **topicDetails**: 主题分类可能为空
4. **regionRestriction**: 地区限制信息可能不存在
5. **contentRating**: 内容分级信息复杂，包含多个国家/组织的分级

## 🔄 数据更新频率

- 统计数据 (观看数、点赞数等): 实时或近实时更新
- 基本信息 (标题、描述等): 创作者修改后立即更新
- 状态信息: 根据视频处理状态实时更新

## 📝 使用建议

1. 根据需要选择合适的字段，避免不必要的配额消耗
2. 对于批量处理，建议使用分页和延迟机制
3. 缓存不经常变化的数据 (如基本信息)
4. 监控API配额使用情况
5. 处理可能为空的字段 (如tags、topicDetails等)

## 🌐 相关链接

- [YouTube Data API v3 官方文档](https://developers.google.com/youtube/v3/docs/)
- [视频资源文档](https://developers.google.com/youtube/v3/docs/videos)
- [搜索资源文档](https://developers.google.com/youtube/v3/docs/search)
- [配额和限制](https://developers.google.com/youtube/v3/getting-started#quota)