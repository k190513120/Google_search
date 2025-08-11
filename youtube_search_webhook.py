# -*- coding: utf-8 -*-
"""
YouTube搜索API - GitHub Webhook版本
用于部署到GitHub Actions，通过webhook触发YouTube视频搜索

功能：
- 接收用户输入的搜索关键词和webhook URL
- 调用YouTube Data API搜索视频
- 获取视频详细统计信息
- 将结果发送到指定的webhook（如飞书多维表格）
"""

import os
import sys
import json
import time
import requests
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime

def send_to_webhook(video_data, webhook_url):
    """发送视频数据到webhook"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'YouTube-Search-Bot/2.0'
        }
        
        response = requests.post(
            webhook_url, 
            json=video_data, 
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook发送成功: {response.status_code}")
            return True
        else:
            print(f"❌ Webhook发送失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook发送异常: {e}")
        return False

def search_youtube_videos(api_key, search_query, max_results=25, webhook_url=None):
    """搜索YouTube视频并返回结果"""
    
    # API配置
    api_service_name = "youtube"
    api_version = "v3"
    
    try:
        # 创建YouTube API客户端
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=api_key
        )

        # 构建搜索请求
        search_request = youtube.search().list(
            part="snippet",
            q=search_query,
            maxResults=max_results,
            order="viewCount",
            type="video"  # 只搜索视频
        )
    
        # 执行搜索请求
        print(f"🔍 正在搜索: {search_query}")
        search_response = search_request.execute()
        print("✅ 搜索请求成功！")
        
        # 收集视频ID
        video_ids = []
        for item in search_response.get('items', []):
            video_id = item.get('id', {}).get('videoId')
            if video_id:
                video_ids.append(video_id)
        
        if not video_ids:
            print("❌ 未找到任何视频")
            return []
        
        # 获取视频详细统计信息
        print(f"📊 正在获取 {len(video_ids)} 个视频的详细信息...")
        videos_request = youtube.videos().list(
            part="snippet,statistics,contentDetails,status,recordingDetails,topicDetails",
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()
        
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
        
        # 处理搜索结果
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
                    # 合并搜索snippet和详细snippet的信息
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
            
            # 打印视频详细信息
            print(f"\n{'='*60}")
            print(f"{i}. 【{video_data['snippet']['title']}】")
            print(f"   视频ID: {video_data['basic_info']['video_id']}")
            print(f"   频道: {video_data['snippet']['channel_title']}")
            print(f"   发布时间: {video_data['snippet']['published_at']}")
            print(f"   分类ID: {video_data['snippet']['category_id']}")
            print(f"   标签: {', '.join(video_data['snippet']['tags'][:5]) if video_data['snippet']['tags'] else '无'}")
            print(f"   默认语言: {video_data['snippet']['default_language']}")
            print(f"   \n📊 统计数据:")
            print(f"   观看次数: {video_data['statistics']['view_count']:,}")
            print(f"   点赞数: {video_data['statistics']['like_count']:,}")
            print(f"   评论数: {video_data['statistics']['comment_count']:,}")
            print(f"   \n🎬 内容详情:")
            print(f"   时长: {video_data['content_details']['duration']}")
            print(f"   清晰度: {video_data['content_details']['definition']}")
            print(f"   字幕: {video_data['content_details']['caption']}")
            print(f"   许可内容: {video_data['content_details']['licensed_content']}")
            print(f"   \n🔒 状态信息:")
            print(f"   上传状态: {video_data['status']['upload_status']}")
            print(f"   隐私状态: {video_data['status']['privacy_status']}")
            print(f"   许可证: {video_data['status']['license']}")
            print(f"   可嵌入: {video_data['status']['embeddable']}")
            print(f"   儿童内容: {video_data['status']['made_for_kids']}")
            if video_data['topic_details']['topic_categories']:
                print(f"   \n🏷️ 主题分类: {', '.join(video_data['topic_details']['topic_categories'][:3])}")
            
            # 发送到webhook（如果提供了URL）
            if webhook_url:
                print(f"   \n📤 发送到webhook...")
                send_success = send_to_webhook(video_data, webhook_url)
                if send_success:
                    print(f"   ✅ 发送成功")
                else:
                    print(f"   ❌ 发送失败")
                
                # 添加延迟避免请求过于频繁
                time.sleep(0.5)
        
        print(f"\n🎉 处理完成！共处理 {len(processed_videos)} 个视频")
        return processed_videos
        
    except googleapiclient.errors.HttpError as e:
        error_msg = f"YouTube API错误 {e.resp.status}: {e.content.decode('utf-8')}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"搜索过程中发生错误: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def main():
    """主函数 - 支持命令行参数和环境变量"""
    
    # 从环境变量或命令行参数获取配置
    api_key = os.getenv('YOUTUBE_API_KEY')
    search_query = os.getenv('SEARCH_QUERY')
    webhook_url = os.getenv('WEBHOOK_URL')
    max_results = int(os.getenv('MAX_RESULTS', '25'))
    
    # 命令行参数优先级更高
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
    if len(sys.argv) > 2:
        webhook_url = sys.argv[2]
    if len(sys.argv) > 3:
        api_key = sys.argv[3]
    if len(sys.argv) > 4:
        max_results = int(sys.argv[4])
    
    # 验证必需参数
    if not api_key:
        print("❌ 错误: 未提供YouTube API密钥")
        print("请设置环境变量 YOUTUBE_API_KEY 或作为命令行参数传入")
        sys.exit(1)
    
    if not search_query:
        print("❌ 错误: 未提供搜索关键词")
        print("请设置环境变量 SEARCH_QUERY 或作为命令行参数传入")
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 YouTube搜索API - GitHub Webhook版本")
    print("=" * 60)
    print(f"🔑 API密钥: {'已设置' if api_key else '未设置'}")
    print(f"🔍 搜索关键词: {search_query}")
    print(f"📤 Webhook URL: {'已设置' if webhook_url else '未设置'}")
    print(f"📊 最大结果数: {max_results}")
    print("=" * 60)
    
    try:
        # 执行搜索
        results = search_youtube_videos(
            api_key=api_key,
            search_query=search_query,
            max_results=max_results,
            webhook_url=webhook_url
        )
        
        # 输出结果摘要
        if results:
            print(f"\n📋 搜索结果摘要:")
            for i, video in enumerate(results[:5], 1):  # 显示前5个结果
                basic_info = video['basic_info']
                stats = video['statistics']
                print(f"{i}. {basic_info['title'][:60]}...")
                print(f"   📺 频道: {basic_info['channel_title']}")
                print(f"   👀 观看: {stats['view_count']:,} | 👍 点赞: {stats['like_count']:,}")
                print(f"   🔗 链接: {basic_info['video_url']}")
                print()
        
        # 如果没有webhook，将结果保存到文件
        if not webhook_url:
            output_file = f"youtube_search_results_{int(time.time())}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {output_file}")
        
        print("\n🎉 任务完成！")
        
    except Exception as e:
        print(f"\n💥 任务失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()