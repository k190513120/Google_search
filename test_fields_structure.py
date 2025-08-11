#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试YouTube API字段结构
验证所有字段都已正确包含在数据结构中
"""

import json
from datetime import datetime

def create_mock_youtube_data():
    """创建模拟的YouTube API响应数据"""
    
    # 模拟搜索响应
    search_response = {
        'items': [{
            'kind': 'youtube#searchResult',
            'etag': 'mock_etag_search',
            'id': {
                'kind': 'youtube#video',
                'videoId': 'mock_video_id_123'
            },
            'snippet': {
                'publishedAt': '2024-01-15T10:30:00Z',
                'channelId': 'UC_mock_channel_id',
                'title': 'HONOR 400 测试视频标题',
                'description': '这是一个测试视频的描述内容...',
                'thumbnails': {
                    'default': {'url': 'https://example.com/default.jpg', 'width': 120, 'height': 90},
                    'medium': {'url': 'https://example.com/medium.jpg', 'width': 320, 'height': 180},
                    'high': {'url': 'https://example.com/high.jpg', 'width': 480, 'height': 360}
                },
                'channelTitle': '测试频道名称',
                'liveBroadcastContent': 'none'
            }
        }]
    }
    
    # 模拟视频详情响应
    videos_response = {
        'items': [{
            'kind': 'youtube#video',
            'etag': 'mock_etag_video',
            'id': 'mock_video_id_123',
            'snippet': {
                'publishedAt': '2024-01-15T10:30:00Z',
                'channelId': 'UC_mock_channel_id',
                'title': 'HONOR 400 测试视频标题',
                'description': '这是一个完整的测试视频描述内容，包含更多详细信息...',
                'thumbnails': {
                    'default': {'url': 'https://example.com/default.jpg', 'width': 120, 'height': 90},
                    'medium': {'url': 'https://example.com/medium.jpg', 'width': 320, 'height': 180},
                    'high': {'url': 'https://example.com/high.jpg', 'width': 480, 'height': 360},
                    'standard': {'url': 'https://example.com/standard.jpg', 'width': 640, 'height': 480},
                    'maxres': {'url': 'https://example.com/maxres.jpg', 'width': 1280, 'height': 720}
                },
                'channelTitle': '测试频道名称',
                'tags': ['HONOR', '400', '智能手机', '测评', '科技'],
                'categoryId': '28',
                'liveBroadcastContent': 'none',
                'defaultLanguage': 'zh-CN',
                'localized': {
                    'title': 'HONOR 400 测试视频标题',
                    'description': '本地化描述内容'
                },
                'defaultAudioLanguage': 'zh-CN',
                'publishTime': '2024-01-15T10:30:00Z'
            },
            'statistics': {
                'viewCount': '125430',
                'likeCount': '3420',
                'dislikeCount': '45',
                'commentCount': '892',
                'favoriteCount': '0'
            },
            'contentDetails': {
                'duration': 'PT8M32S',
                'dimension': '2d',
                'definition': 'hd',
                'caption': 'true',
                'licensedContent': True,
                'regionRestriction': {
                    'allowed': ['US', 'CA', 'GB'],
                    'blocked': ['CN', 'RU']
                },
                'contentRating': {
                    'ytRating': 'ytAgeRestricted'
                },
                'projection': 'rectangular',
                'hasCustomThumbnail': True
            },
            'status': {
                'uploadStatus': 'processed',
                'failureReason': None,
                'rejectionReason': None,
                'privacyStatus': 'public',
                'publishAt': None,
                'license': 'youtube',
                'embeddable': True,
                'publicStatsViewable': True,
                'madeForKids': False,
                'selfDeclaredMadeForKids': False
            },
            'recordingDetails': {
                'locationDescription': '北京市朝阳区',
                'location': {
                    'latitude': 39.9042,
                    'longitude': 116.4074,
                    'altitude': 43.5
                },
                'recordingDate': '2024-01-14T15:20:00Z'
            },
            'topicDetails': {
                'topicIds': ['/m/07c1v', '/m/0bzvm2'],
                'relevantTopicIds': ['/m/07c1v', '/m/0bzvm2', '/m/019_rr'],
                'topicCategories': [
                    'https://en.wikipedia.org/wiki/Technology',
                    'https://en.wikipedia.org/wiki/Consumer_electronics'
                ]
            }
        }]
    }
    
    return search_response, videos_response

def process_mock_data(search_response, videos_response, search_query="HONOR 400"):
    """处理模拟数据，生成完整的视频数据结构"""
    
    # 构建视频详细信息字典
    video_details = {}
    for video in videos_response.get('items', []):
        video_id = video.get('id')
        if video_id:
            video_details[video_id] = {
                'snippet': video.get('snippet', {}),
                'statistics': video.get('statistics', {}),
                'contentDetails': video.get('contentDetails', {}),
                'status': video.get('status', {}),
                'recordingDetails': video.get('recordingDetails', {}),
                'topicDetails': video.get('topicDetails', {})
            }
    
    processed_videos = []
    
    for i, item in enumerate(search_response['items'], 1):
        # 基本信息
        video_id = item.get('id', {}).get('videoId', 'N/A')
        snippet = item.get('snippet', {})
        
        # 获取所有详细信息
        video_snippet = video_details.get(video_id, {}).get('snippet', {})
        stats = video_details.get(video_id, {}).get('statistics', {})
        content_details = video_details.get(video_id, {}).get('contentDetails', {})
        status = video_details.get(video_id, {}).get('status', {})
        recording_details = video_details.get(video_id, {}).get('recordingDetails', {})
        topic_details = video_details.get(video_id, {}).get('topicDetails', {})
        
        # 构建完整的视频数据结构
        video_data = {
            "basic_info": {
                "kind": item.get('kind', 'N/A'),
                "etag": item.get('etag', 'N/A'),
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id != 'N/A' else 'N/A'
            },
            "snippet": {
                "published_at": snippet.get('publishedAt', 'N/A'),
                "channel_id": snippet.get('channelId', 'N/A'),
                "title": snippet.get('title', 'N/A'),
                "description": snippet.get('description', ''),
                "channel_title": snippet.get('channelTitle', 'N/A'),
                "tags": snippet.get('tags', []),
                "category_id": snippet.get('categoryId', 'N/A'),
                "live_broadcast_content": snippet.get('liveBroadcastContent', 'N/A'),
                "default_language": snippet.get('defaultLanguage', 'N/A'),
                "default_audio_language": snippet.get('defaultAudioLanguage', 'N/A'),
                "localized": snippet.get('localized', {}),
                "publish_time": video_snippet.get('publishTime', snippet.get('publishTime', 'N/A'))
            },
            "statistics": {
                "view_count": int(stats.get('viewCount', 0)) if stats.get('viewCount', '0').isdigit() else 0,
                "like_count": int(stats.get('likeCount', 0)) if stats.get('likeCount', '0').isdigit() else 0,
                "dislike_count": int(stats.get('dislikeCount', 0)) if stats.get('dislikeCount', '0').isdigit() else 0,
                "comment_count": int(stats.get('commentCount', 0)) if stats.get('commentCount', '0').isdigit() else 0,
                "favorite_count": int(stats.get('favoriteCount', 0)) if stats.get('favoriteCount', '0').isdigit() else 0
            },
            "content_details": {
                "duration": content_details.get('duration', 'N/A'),
                "dimension": content_details.get('dimension', 'N/A'),
                "definition": content_details.get('definition', 'N/A'),
                "caption": content_details.get('caption', 'N/A'),
                "licensed_content": content_details.get('licensedContent', 'N/A'),
                "region_restriction": content_details.get('regionRestriction', {}),
                "content_rating": content_details.get('contentRating', {}),
                "projection": content_details.get('projection', 'N/A'),
                "has_custom_thumbnail": content_details.get('hasCustomThumbnail', 'N/A')
            },
            "status": {
                "upload_status": status.get('uploadStatus', 'N/A'),
                "failure_reason": status.get('failureReason', 'N/A'),
                "rejection_reason": status.get('rejectionReason', 'N/A'),
                "privacy_status": status.get('privacyStatus', 'N/A'),
                "publish_at": status.get('publishAt', 'N/A'),
                "license": status.get('license', 'N/A'),
                "embeddable": status.get('embeddable', 'N/A'),
                "public_stats_viewable": status.get('publicStatsViewable', 'N/A'),
                "made_for_kids": status.get('madeForKids', 'N/A'),
                "self_declared_made_for_kids": status.get('selfDeclaredMadeForKids', 'N/A')
            },
            "thumbnails": {
                "default": snippet.get('thumbnails', {}).get('default', {}),
                "medium": snippet.get('thumbnails', {}).get('medium', {}),
                "high": snippet.get('thumbnails', {}).get('high', {}),
                "standard": snippet.get('thumbnails', {}).get('standard', {}),
                "maxres": snippet.get('thumbnails', {}).get('maxres', {})
            },
            "recording_details": {
                "location_description": recording_details.get('locationDescription', 'N/A'),
                "location": recording_details.get('location', {}),
                "recording_date": recording_details.get('recordingDate', 'N/A')
            },
            "topic_details": {
                "topic_ids": topic_details.get('topicIds', []),
                "relevant_topic_ids": topic_details.get('relevantTopicIds', []),
                "topic_categories": topic_details.get('topicCategories', [])
            },
            "search_metadata": {
                "search_query": search_query,
                "result_index": i,
                "timestamp": datetime.now().isoformat(),
                "total_results": len(search_response['items']),
                "search_kind": item.get('id', {}).get('kind', 'N/A')
            }
        }
        
        processed_videos.append(video_data)
    
    return processed_videos

def print_field_coverage():
    """打印字段覆盖情况"""
    print("\n🔍 YouTube API 字段覆盖检查")
    print("="*60)
    
    # 根据YouTube API文档列出的所有可能字段
    expected_fields = {
        'basic_info': ['kind', 'etag', 'video_id', 'video_url'],
        'snippet': [
            'published_at', 'channel_id', 'title', 'description', 'channel_title',
            'tags', 'category_id', 'live_broadcast_content', 'default_language',
            'default_audio_language', 'localized', 'publish_time'
        ],
        'statistics': [
            'view_count', 'like_count', 'dislike_count', 'comment_count', 'favorite_count'
        ],
        'content_details': [
            'duration', 'dimension', 'definition', 'caption', 'licensed_content',
            'region_restriction', 'content_rating', 'projection', 'has_custom_thumbnail'
        ],
        'status': [
            'upload_status', 'failure_reason', 'rejection_reason', 'privacy_status',
            'publish_at', 'license', 'embeddable', 'public_stats_viewable',
            'made_for_kids', 'self_declared_made_for_kids'
        ],
        'thumbnails': ['default', 'medium', 'high', 'standard', 'maxres'],
        'recording_details': ['location_description', 'location', 'recording_date'],
        'topic_details': ['topic_ids', 'relevant_topic_ids', 'topic_categories'],
        'search_metadata': [
            'search_query', 'result_index', 'timestamp', 'total_results', 'search_kind'
        ]
    }
    
    # 创建测试数据
    search_response, videos_response = create_mock_youtube_data()
    processed_videos = process_mock_data(search_response, videos_response)
    
    if processed_videos:
        video_data = processed_videos[0]
        
        print("\n✅ 已包含的字段:")
        total_fields = 0
        covered_fields = 0
        
        for section, fields in expected_fields.items():
            print(f"\n📋 {section.upper()}:")
            if section in video_data:
                for field in fields:
                    total_fields += 1
                    if field in video_data[section]:
                        covered_fields += 1
                        print(f"   ✅ {field}: {type(video_data[section][field]).__name__}")
                    else:
                        print(f"   ❌ {field}: 缺失")
            else:
                print(f"   ❌ 整个 {section} 部分缺失")
                total_fields += len(fields)
        
        coverage_rate = (covered_fields / total_fields) * 100
        print(f"\n📊 字段覆盖率: {covered_fields}/{total_fields} ({coverage_rate:.1f}%)")
        
        if coverage_rate >= 95:
            print("🎉 字段覆盖率优秀！")
        elif coverage_rate >= 80:
            print("👍 字段覆盖率良好！")
        else:
            print("⚠️ 字段覆盖率需要改进")

def main():
    """主函数"""
    print("🧪 YouTube API 字段结构测试")
    print("="*60)
    
    # 创建模拟数据
    search_response, videos_response = create_mock_youtube_data()
    
    # 处理数据
    processed_videos = process_mock_data(search_response, videos_response)
    
    if processed_videos:
        video_data = processed_videos[0]
        
        # 打印示例数据结构
        print("\n📄 示例视频数据结构:")
        print("-" * 40)
        print(f"标题: {video_data['snippet']['title']}")
        print(f"频道: {video_data['snippet']['channel_title']}")
        print(f"观看次数: {video_data['statistics']['view_count']:,}")
        print(f"点赞数: {video_data['statistics']['like_count']:,}")
        print(f"时长: {video_data['content_details']['duration']}")
        print(f"标签: {', '.join(video_data['snippet']['tags'])}")
        print(f"主题分类: {len(video_data['topic_details']['topic_categories'])} 个")
        
        # 保存完整数据到JSON文件
        with open('sample_youtube_data.json', 'w', encoding='utf-8') as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 完整数据结构已保存到: sample_youtube_data.json")
    
    # 检查字段覆盖情况
    print_field_coverage()
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    main()