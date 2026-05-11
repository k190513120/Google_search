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
from datetime import datetime, timezone
from googleapiclient.http import build_http

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

def get_video_comments(api_key, video_id, max_comments=50, webhook_url=None):
    """获取YouTube视频的热门评论"""
    
    # API配置
    api_service_name = "youtube"
    api_version = "v3"
    
    try:
        # 检查是否在GitHub Actions环境中运行
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        if is_github_actions:
            # GitHub Actions环境，直接创建客户端（无需代理）
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=api_key
            )
            print("🚀 GitHub Actions环境，直接连接YouTube API")
        else:
            # 本地环境，检查是否需要使用代理
            http_proxy = os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('HTTPS_PROXY')
            socks_proxy = os.getenv('SOCKS_PROXY')
            
            proxy_url = socks_proxy or https_proxy or http_proxy
            
            if proxy_url:
                # 使用代理创建HTTP客户端
                import httplib2
                import socks
                
                if socks_proxy:
                    # SOCKS代理
                    proxy_parts = socks_proxy.replace('socks5://', '').replace('socks4://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 1080
                    proxy_type = socks.PROXY_TYPE_SOCKS5 if 'socks5' in socks_proxy else socks.PROXY_TYPE_SOCKS4
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=proxy_type,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                else:
                    # HTTP/HTTPS代理
                    proxy_parts = proxy_url.replace('http://', '').replace('https://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 8080
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key, http=http
                )
                print(f"🌐 使用代理: {proxy_url}")
            else:
                # 创建YouTube API客户端（无代理）
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key
                )
        
        print(f"💬 正在获取视频 {video_id} 的评论...")
        
        # 首先获取视频基本信息
        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        video_response = video_request.execute()
        
        if not video_response.get('items'):
            print("❌ 视频不存在或无法访问")
            return None
            
        video_info = video_response['items'][0]
        video_snippet = video_info.get('snippet', {})
        video_stats = video_info.get('statistics', {})
        
        # 获取评论
        comments_request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=min(max_comments, 100),  # YouTube API最大支持100条
            order="relevance"  # 按相关性排序（通常包含点赞数）
        )
        
        comments_response = comments_request.execute()
        
        # 处理评论数据
        comments_data = []
        for item in comments_response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            
            comment_data = {
                'author_name': comment.get('authorDisplayName', ''),
                'author_channel_url': comment.get('authorChannelUrl', ''),
                'text': comment.get('textDisplay', ''),
                'like_count': int(comment.get('likeCount', 0)),
                'published_at': comment.get('publishedAt', ''),
                'updated_at': comment.get('updatedAt', ''),
                'reply_count': item['snippet'].get('totalReplyCount', 0)
            }
            comments_data.append(comment_data)
        
        # 按点赞数排序
        comments_data.sort(key=lambda x: x['like_count'], reverse=True)
        
        # 限制返回数量
        comments_data = comments_data[:max_comments]
        
        # 构建完整结果
        result = {
            'video_info': {
                'video_id': video_id,
                'title': video_snippet.get('title', ''),
                'channel_title': video_snippet.get('channelTitle', ''),
                'channel_id': video_snippet.get('channelId', ''),
                'published_at': video_snippet.get('publishedAt', ''),
                'description': video_snippet.get('description', '')[:500] + '...' if len(video_snippet.get('description', '')) > 500 else video_snippet.get('description', ''),
                'view_count': int(video_stats.get('viewCount', 0)),
                'like_count': int(video_stats.get('likeCount', 0)),
                'comment_count': int(video_stats.get('commentCount', 0)),
                'video_url': f'https://www.youtube.com/watch?v={video_id}'
            },
            'comments': comments_data,
            'total_comments_fetched': len(comments_data),
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 成功获取 {len(comments_data)} 条评论")
        
        # 如果提供了webhook URL，发送结果
        if webhook_url:
            print(f"📤 正在发送结果到webhook...")
            send_success = send_to_webhook(result, webhook_url)
            if send_success:
                print("✅ 评论数据已成功发送到webhook")
            else:
                print("❌ 评论数据发送到webhook失败")
        
        return result
        
    except googleapiclient.errors.HttpError as e:
        error_details = json.loads(e.content.decode('utf-8'))
        error_reason = error_details.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
        
        if error_reason == 'commentsDisabled':
            print("❌ 该视频的评论功能已被禁用")
        elif error_reason == 'videoNotFound':
            print("❌ 视频不存在")
        else:
            print(f"❌ 获取评论时发生API错误: {e}")
        
        return {
            'video_info': {'video_id': video_id, 'error': f'API错误: {error_reason}'},
            'comments': [],
            'total_comments_fetched': 0,
            'fetch_timestamp': datetime.now().isoformat(),
            'error': str(e)
        }
        
    except Exception as e:
        print(f"❌ 获取评论时发生错误: {e}")
        return {
            'video_info': {'video_id': video_id, 'error': str(e)},
            'comments': [],
            'total_comments_fetched': 0,
            'fetch_timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def get_channel_videos(api_key, handle, max_results=50, webhook_url=None, batch_size=100):
    """获取指定频道的所有视频信息（通过handle）"""
    
    # API配置
    api_service_name = "youtube"
    api_version = "v3"
    
    try:
        # 检查是否在GitHub Actions环境中运行
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        if is_github_actions:
            # GitHub Actions环境，直接创建客户端（无需代理）
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=api_key
            )
            print("🚀 GitHub Actions环境，直接连接YouTube API")
        else:
            # 本地环境，检查是否需要使用代理
            http_proxy = os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('HTTPS_PROXY')
            socks_proxy = os.getenv('SOCKS_PROXY')
            
            proxy_url = socks_proxy or https_proxy or http_proxy
            
            if proxy_url:
                # 使用代理创建HTTP客户端
                import httplib2
                import socks
                
                if socks_proxy:
                    # SOCKS代理
                    proxy_parts = socks_proxy.replace('socks5://', '').replace('socks4://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 1080
                    proxy_type = socks.PROXY_TYPE_SOCKS5 if 'socks5' in socks_proxy else socks.PROXY_TYPE_SOCKS4
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=proxy_type,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                else:
                    # HTTP/HTTPS代理
                    proxy_parts = proxy_url.replace('http://', '').replace('https://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 8080
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key, http=http
                )
                print(f"🌐 使用代理: {proxy_url}")
            else:
                # 创建YouTube API客户端（无代理）
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key
                )
        
        print(f"📺 正在获取频道 {handle} 的视频信息...")
        
        # 处理handle格式：支持YouTube链接和直接handle
        if handle.startswith('https://www.youtube.com/@'):
            # 从YouTube链接中提取handle
            processed_handle = handle.replace('https://www.youtube.com/', '')
            print(f"🔗 从链接提取handle: {handle} -> {processed_handle}")
        elif handle.startswith('@'):
            # 直接使用@handle格式
            processed_handle = handle
            print(f"🔍 使用handle: {processed_handle}")
        else:
            # 兼容旧格式：直接添加@前缀
            processed_handle = '@' + handle
            print(f"🔧 添加@前缀: {handle} -> {processed_handle}")
        
        # 直接通过forHandle参数获取频道信息
        channel_request = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            forHandle=processed_handle
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get('items'):
            print("❌ 频道不存在或无法访问")
            return None
            
        channel_info = channel_response['items'][0]
        channel_snippet = channel_info.get('snippet', {})
        channel_stats = channel_info.get('statistics', {})
        
        # 获取频道的上传播放列表ID
        uploads_playlist_id = channel_info.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        
        if not uploads_playlist_id:
            print("❌ 无法获取频道的上传播放列表")
            return None
        
        # 获取播放列表中的视频
        all_videos = []
        next_page_token = None
        page_count = 0
        total_fetched = 0
        
        print(f"📊 开始获取频道视频，目标数量: {max_results}")
        
        while len(all_videos) < max_results:
            page_count += 1
            remaining_results = max_results - len(all_videos)
            current_max_results = min(50, remaining_results)  # YouTube API单次最大50条
            
            print(f"📄 正在获取第 {page_count} 页，本页目标: {current_max_results} 条")
            
            playlist_request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=current_max_results,
                pageToken=next_page_token
            )
            
            playlist_response = playlist_request.execute()
            
            # 收集视频ID
            video_ids = []
            for item in playlist_response.get('items', []):
                video_id = item.get('contentDetails', {}).get('videoId')
                if video_id:
                    video_ids.append(video_id)
            
            if not video_ids:
                print(f"⚠️ 第 {page_count} 页没有找到视频，停止获取")
                break
            
            print(f"✅ 第 {page_count} 页获取到 {len(video_ids)} 个视频ID")
            
            # 获取视频详细信息
            videos_request = youtube.videos().list(
                part="snippet,statistics,contentDetails,status,recordingDetails,topicDetails",
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()
            
            # 处理视频数据
            for video in videos_response.get('items', []):
                video_snippet = video.get('snippet', {})
                video_stats = video.get('statistics', {})
                video_content = video.get('contentDetails', {})
                video_status = video.get('status', {})
                video_recording = video.get('recordingDetails', {})
                video_topics = video.get('topicDetails', {})

                # 检查发布日期是否晚于2023年12月31日
                published_at_str = video_snippet.get('publishedAt', '')
                if published_at_str:
                    published_at_dt = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    if published_at_dt <= datetime(2023, 12, 31, 23, 59, 59, tzinfo=timezone.utc):
                        print(f"⚠️ 视频 '{video_snippet.get('title', '')}' 发布于 {published_at_str}，早于2024年，跳过。")
                        continue

                video_data = {
                    'video_id': video.get('id', ''),
                    'title': video_snippet.get('title', ''),
                    'description': video_snippet.get('description', ''),
                    'published_at': video_snippet.get('publishedAt', ''),
                    'duration': video_content.get('duration', ''),
                    'view_count': int(video_stats.get('viewCount', 0)),
                    'like_count': int(video_stats.get('likeCount', 0)),
                    'comment_count': int(video_stats.get('commentCount', 0)),
                    'privacy_status': video_status.get('privacyStatus', ''),
                    'video_url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                    'thumbnail_url': video_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'tags': video_snippet.get('tags', []),
                    'category_id': video_snippet.get('categoryId', ''),
                    'default_language': video_snippet.get('defaultLanguage', ''),
                    'definition': video_content.get('definition', ''),
                    'caption': video_content.get('caption', ''),
                    # 新增字段
                    'thumbnails': video_snippet.get('thumbnails', {}),  # 完整缩略图信息
                    'live_broadcast_content': video_snippet.get('liveBroadcastContent', ''),
                    'default_audio_language': video_snippet.get('defaultAudioLanguage', ''),
                    'dimension': video_content.get('dimension', ''),
                    'projection': video_content.get('projection', ''),
                    'has_custom_thumbnail': video_content.get('hasCustomThumbnail', False),
                    'upload_status': video_status.get('uploadStatus', ''),
                    'license': video_status.get('license', ''),
                    'embeddable': video_status.get('embeddable', True),
                    'public_stats_viewable': video_status.get('publicStatsViewable', True),
                    'made_for_kids': video_status.get('madeForKids', False),
                    # 录制详情（可能为空）
                    'recording_date': video_recording.get('recordingDate', ''),
                    'location_description': video_recording.get('locationDescription', ''),
                    'location': video_recording.get('location', {}),
                    # 主题详情（可能为空）
                    'topic_ids': video_topics.get('topicIds', []),
                    'topic_categories': video_topics.get('topicCategories', [])
                }
                all_videos.append(video_data)
            
            # 检查是否有下一页
            next_page_token = playlist_response.get('nextPageToken')
            total_fetched = len(all_videos)
            
            print(f"📈 当前已获取 {total_fetched} 个视频")
            
            # 检查是否需要分批发送webhook
            if webhook_url and len(all_videos) >= batch_size:
                # 计算需要发送的批次
                batches_to_send = len(all_videos) // batch_size
                for batch_num in range(batches_to_send):
                    start_idx = batch_num * batch_size
                    end_idx = start_idx + batch_size
                    batch_videos = all_videos[start_idx:end_idx]
                    
                    # 构建批次数据
                    batch_result = {
                        'channel_info': {
                            'channel_id': channel_info.get('id', ''),
                            'handle': handle,
                            'title': channel_snippet.get('title', ''),
                            'description': channel_snippet.get('description', ''),
                            'custom_url': channel_snippet.get('customUrl', ''),
                            'published_at': channel_snippet.get('publishedAt', ''),
                            'country': channel_snippet.get('country', ''),
                            'thumbnail_url': channel_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                            'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                            'video_count': int(channel_stats.get('videoCount', 0)),
                            'view_count': int(channel_stats.get('viewCount', 0)),
                            'channel_url': f"https://www.youtube.com/channel/{channel_info.get('id', '')}"
                        },
                        'videos': batch_videos,
                        'batch_info': {
                            'batch_number': batch_num + 1,
                            'batch_size': len(batch_videos),
                            'total_videos_in_batch': len(batch_videos),
                            'is_final_batch': False
                        },
                        'total_videos_fetched': total_fetched,
                        'fetch_timestamp': datetime.now().isoformat()
                    }
                    
                    print(f"📤 发送第 {batch_num + 1} 批数据到webhook ({len(batch_videos)} 个视频)")
                    success = send_to_webhook(batch_result, webhook_url)
                    if success:
                        print(f"✅ 第 {batch_num + 1} 批webhook发送成功")
                    else:
                        print(f"❌ 第 {batch_num + 1} 批webhook发送失败")
                    
                    # 短暂延迟避免webhook服务器压力
                    time.sleep(1)
                
                # 移除已发送的视频，保留未发送的部分
                remaining_videos = all_videos[batches_to_send * batch_size:]
                all_videos = remaining_videos
                print(f"📊 已发送 {batches_to_send} 批数据，剩余 {len(all_videos)} 个视频待处理")
            
            if not next_page_token:
                print(f"📄 已到达最后一页，总共获取了 {total_fetched} 个视频")
                break
            else:
                print(f"➡️ 存在下一页，继续获取...")
                
            # 如果已经获取足够的视频，退出循环
            if len(all_videos) >= max_results:
                print(f"🎯 已达到目标数量 {max_results}，停止获取")
                break
        
        # 按观看数排序
        all_videos.sort(key=lambda x: x['view_count'], reverse=True)
        
        # 限制返回数量
        all_videos = all_videos[:max_results]
        
        print(f"📊 分页获取完成统计:")
        print(f"   - 总页数: {page_count}")
        print(f"   - 实际获取: {len(all_videos)} 个视频")
        print(f"   - 目标数量: {max_results}")
        print(f"   - 已按观看数排序")
        
        # 获取实际的频道ID（从API响应中获取）
        actual_channel_id = channel_info.get('id', '')
        
        # 构建完整结果
        result = {
            'channel_info': {
                'channel_id': actual_channel_id,
                'handle': handle,
                'title': channel_snippet.get('title', ''),
                'description': channel_snippet.get('description', ''),
                'custom_url': channel_snippet.get('customUrl', ''),
                'published_at': channel_snippet.get('publishedAt', ''),
                'country': channel_snippet.get('country', ''),  # 添加这行
                'thumbnail_url': channel_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                'video_count': int(channel_stats.get('videoCount', 0)),
                'view_count': int(channel_stats.get('viewCount', 0)),
                'channel_url': f"https://www.youtube.com/channel/{actual_channel_id}"
            },
            'videos': all_videos,
            'total_videos_fetched': len(all_videos),
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 成功获取频道 {channel_snippet.get('title', handle)} 的 {len(all_videos)} 个视频")
        
        # 发送剩余的视频到webhook（最后一批）
        if webhook_url and all_videos:
            # 构建最后一批数据
            final_batch_result = {
                'channel_info': {
                    'channel_id': actual_channel_id,
                    'handle': handle,
                    'title': channel_snippet.get('title', ''),
                    'description': channel_snippet.get('description', ''),
                    'custom_url': channel_snippet.get('customUrl', ''),
                    'published_at': channel_snippet.get('publishedAt', ''),
                    'country': channel_snippet.get('country', ''),
                    'thumbnail_url': channel_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                    'video_count': int(channel_stats.get('videoCount', 0)),
                    'view_count': int(channel_stats.get('viewCount', 0)),
                    'channel_url': f"https://www.youtube.com/channel/{actual_channel_id}"
                },
                'videos': all_videos,
                'batch_info': {
                    'batch_number': 'final',
                    'batch_size': len(all_videos),
                    'total_videos_in_batch': len(all_videos),
                    'is_final_batch': True
                },
                'total_videos_fetched': len(all_videos),
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            print(f"📤 发送最后一批数据到webhook ({len(all_videos)} 个视频)")
            success = send_to_webhook(final_batch_result, webhook_url)
            if success:
                print("✅ 最后一批webhook发送成功")
            else:
                print("❌ 最后一批webhook发送失败")
        
        # 构建完整结果用于返回（不包含batch_info）
        result = {
            'channel_info': {
                'channel_id': actual_channel_id,
                'handle': handle,
                'title': channel_snippet.get('title', ''),
                'description': channel_snippet.get('description', ''),
                'custom_url': channel_snippet.get('customUrl', ''),
                'published_at': channel_snippet.get('publishedAt', ''),
                'country': channel_snippet.get('country', ''),
                'thumbnail_url': channel_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                'video_count': int(channel_stats.get('videoCount', 0)),
                'view_count': int(channel_stats.get('viewCount', 0)),
                'channel_url': f"https://www.youtube.com/channel/{actual_channel_id}"
            },
            'videos': all_videos,
            'total_videos_fetched': len(all_videos),
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except googleapiclient.errors.HttpError as e:
        error_msg = f"YouTube API错误: {e}"
        print(f"❌ {error_msg}")
        return {
            'channel_info': {'handle': handle, 'error': str(e)},
            'videos': [],
            'total_videos_fetched': 0,
            'fetch_timestamp': datetime.now().isoformat(),
            'error': str(e)
        }
        
    except Exception as e:
        print(f"❌ 获取频道视频时发生错误: {e}")
        return {
            'channel_info': {'handle': handle, 'error': str(e)},
            'videos': [],
            'total_videos_fetched': 0,
            'fetch_timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def search_youtube_videos(api_key, search_query, max_results=25, webhook_url=None, published_after=None, published_before=None):
    """搜索YouTube视频并返回结果，支持分页获取更多结果和时间筛选
    
    Args:
        api_key: YouTube API密钥
        search_query: 搜索关键词
        max_results: 最大结果数量
        webhook_url: Webhook回调地址
        published_after: 筛选此时间之后发布的视频 (格式: YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SSZ)
        published_before: 筛选此时间之前发布的视频 (格式: YYYY-MM-DD 或 YYYY-MM-DDTHH:MM:SSZ)
    """
    
    # API配置
    api_service_name = "youtube"
    api_version = "v3"
    
    try:
        # 检查是否在GitHub Actions环境中运行
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        if is_github_actions:
            # GitHub Actions环境，直接创建客户端（无需代理）
            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey=api_key
            )
            print("🚀 GitHub Actions环境，直接连接YouTube API")
        else:
            # 本地环境，检查是否需要使用代理
            http_proxy = os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('HTTPS_PROXY')
            socks_proxy = os.getenv('SOCKS_PROXY')
            
            proxy_url = socks_proxy or https_proxy or http_proxy
            
            if proxy_url:
                # 使用代理创建HTTP客户端
                import httplib2
                import socks
                
                if socks_proxy:
                    # SOCKS代理
                    proxy_parts = socks_proxy.replace('socks5://', '').replace('socks4://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 1080
                    proxy_type = socks.PROXY_TYPE_SOCKS5 if 'socks5' in socks_proxy else socks.PROXY_TYPE_SOCKS4
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=proxy_type,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                else:
                    # HTTP/HTTPS代理
                    proxy_parts = proxy_url.replace('http://', '').replace('https://', '').split(':')
                    proxy_host = proxy_parts[0]
                    proxy_port = int(proxy_parts[1]) if len(proxy_parts) > 1 else 8080
                    
                    http = httplib2.Http(proxy_info=httplib2.ProxyInfo(
                        proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                        proxy_host=proxy_host,
                        proxy_port=proxy_port
                    ))
                
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key, http=http
                )
                print(f"🌐 使用代理: {proxy_url}")
            else:
                # 创建YouTube API客户端（无代理）
                youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey=api_key
                )

        # 分页获取搜索结果
        all_video_ids = []
        next_page_token = None
        search_requests_count = 0
        
        print(f"🔍 正在搜索: {search_query}")
        print(f"📊 目标结果数: {max_results}")
        if published_after:
            print(f"📅 筛选时间范围: {published_after} 之后")
        if published_before:
            print(f"📅 筛选时间范围: {published_before} 之前")
        
        while len(all_video_ids) < max_results:
            # 计算本次请求需要获取的结果数
            remaining_results = max_results - len(all_video_ids)
            current_max_results = min(50, remaining_results)  # YouTube API单次最大50条
            
            # 构建搜索请求参数
            search_params = {
                "part": "snippet",
                "q": search_query,
                "maxResults": current_max_results,
                "order": "viewCount",
                "type": "video",  # 只搜索视频
                "pageToken": next_page_token
            }
            
            # 添加时间筛选参数
            if published_after:
                # 如果只有日期，添加时间部分
                if len(published_after) == 10:  # YYYY-MM-DD格式
                    published_after_formatted = published_after + "T00:00:00Z"
                else:
                    published_after_formatted = published_after
                search_params["publishedAfter"] = published_after_formatted
                
            if published_before:
                # 如果只有日期，添加时间部分
                if len(published_before) == 10:  # YYYY-MM-DD格式
                    published_before_formatted = published_before + "T23:59:59Z"
                else:
                    published_before_formatted = published_before
                search_params["publishedBefore"] = published_before_formatted
            
            # 构建搜索请求
            search_request = youtube.search().list(**search_params)
        
            # 执行搜索请求
            search_response = search_request.execute()
            search_requests_count += 1
            print(f"✅ 第{search_requests_count}次搜索请求成功！获取到 {len(search_response.get('items', []))} 条结果")
            
            # 收集视频ID
            for item in search_response.get('items', []):
                video_id = item.get('id', {}).get('videoId')
                if video_id:
                    all_video_ids.append(video_id)
            
            # 检查是否有下一页
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                print("📄 已到达搜索结果末页")
                break
                
            # 如果已经获取足够的结果，退出循环
            if len(all_video_ids) >= max_results:
                break
        
        # 限制结果数量
        all_video_ids = all_video_ids[:max_results]
        
        if not all_video_ids:
            print("❌ 未找到任何视频")
            return []
            
        print(f"📋 总共收集到 {len(all_video_ids)} 个视频ID")
        print(f"💰 搜索配额消耗: {search_requests_count * 100} 单位")
        
        # 分批获取视频详细信息（YouTube API限制单次最多50个ID）
        all_video_details = []
        batch_size = 50
        videos_requests_count = 0
        
        for i in range(0, len(all_video_ids), batch_size):
            batch_ids = all_video_ids[i:i + batch_size]
            print(f"📋 处理第 {i//batch_size + 1} 批视频 ({len(batch_ids)} 个)")
            
            videos_request = youtube.videos().list(
                part="snippet,statistics,contentDetails,status,recordingDetails,topicDetails",
                id=','.join(batch_ids)
            )
            videos_response = videos_request.execute()
            videos_requests_count += 1
            all_video_details.extend(videos_response.get('items', []))
        
        print(f"💰 视频详情配额消耗: {videos_requests_count * 1} 单位")
        print(f"💰 总配额消耗: {search_requests_count * 100 + videos_requests_count * 1} 单位")
        
        # 构建视频详细信息字典
        video_details = {}
        for video in all_video_details:
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
        
        # 收集所有唯一的频道ID
        unique_channel_ids = set()
        for video in all_video_details:
            channel_id = video.get('snippet', {}).get('channelId')
            if channel_id:
                unique_channel_ids.add(channel_id)
        
        # 批量获取频道信息
        channel_info_dict = {}
        if unique_channel_ids:
            print(f"📺 正在获取 {len(unique_channel_ids)} 个频道的详细信息...")
            
            # 分批获取频道信息（YouTube API限制单次最多50个ID）
            channel_batch_size = 50
            channel_ids_list = list(unique_channel_ids)
            
            for i in range(0, len(channel_ids_list), channel_batch_size):
                batch_channel_ids = channel_ids_list[i:i + channel_batch_size]
                print(f"📋 处理第 {i//channel_batch_size + 1} 批频道 ({len(batch_channel_ids)} 个)")
                
                channels_request = youtube.channels().list(
                    part="snippet,statistics,brandingSettings,status,topicDetails,localizations",
                    id=','.join(batch_channel_ids)
                )
                channels_response = channels_request.execute()
                
                # 处理频道信息
                for channel in channels_response.get('items', []):
                    channel_id = channel.get('id')
                    if channel_id:
                        channel_snippet = channel.get('snippet', {})
                        channel_stats = channel.get('statistics', {})
                        channel_branding = channel.get('brandingSettings', {})
                        channel_status = channel.get('status', {})
                        channel_topics = channel.get('topicDetails', {})
                        
                        channel_info_dict[channel_id] = {
                            'channel_id': channel_id,
                            'title': channel_snippet.get('title', ''),
                            'description': channel_snippet.get('description', ''),
                            'custom_url': channel_snippet.get('customUrl', ''),
                            'published_at': channel_snippet.get('publishedAt', ''),
                            'country': channel_snippet.get('country', ''),
                            'default_language': channel_snippet.get('defaultLanguage', ''),
                            'localized_title': channel_snippet.get('localized', {}).get('title', ''),
                            'localized_description': channel_snippet.get('localized', {}).get('description', ''),
                            'thumbnail_url': channel_snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                            'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
                            'video_count': int(channel_stats.get('videoCount', 0)),
                            'view_count': int(channel_stats.get('viewCount', 0)),
                            'subscriber_count_hidden': channel_stats.get('hiddenSubscriberCount', False),
                            'privacy_status': channel_status.get('privacyStatus', ''),
                            'is_linked': channel_status.get('isLinked', False),
                            'long_uploads_status': channel_status.get('longUploadsStatus', ''),
                            'made_for_kids': channel_status.get('madeForKids', False),
                            'self_declared_made_for_kids': channel_status.get('selfDeclaredMadeForKids', False),
                            'topic_ids': channel_topics.get('topicIds', []),
                            'topic_categories': channel_topics.get('topicCategories', []),
                            'keywords': channel_branding.get('channel', {}).get('keywords', ''),
                            'channel_url': f"https://www.youtube.com/channel/{channel_id}"
                        }
            
            print(f"✅ 成功获取 {len(channel_info_dict)} 个频道的详细信息")
        
        # 处理搜索结果
        processed_videos = []
        
        for i, video_id in enumerate(all_video_ids, 1):
            if video_id not in video_details:
                continue
                
            # 获取视频详细信息
            video = video_details[video_id]
            snippet = video.get('snippet', {})
            
            # 获取所有详细信息
            video_snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            status = video.get('status', {})
            recording_details = video.get('recordingDetails', {})
            topic_details = video.get('topicDetails', {})
            
            # 获取频道信息
            channel_id = snippet.get('channelId', 'N/A')
            channel_info = channel_info_dict.get(channel_id, {})
            
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
                "channel_info": {
                    "channel_id": channel_info.get('channel_id', channel_id),
                    "title": channel_info.get('title', snippet.get('channelTitle', 'N/A')),
                    "description": channel_info.get('description', ''),
                    "custom_url": channel_info.get('custom_url', ''),
                    "published_at": channel_info.get('published_at', ''),
                    "country": channel_info.get('country', ''),
                    "default_language": channel_info.get('default_language', ''),
                    "localized_title": channel_info.get('localized_title', ''),
                    "localized_description": channel_info.get('localized_description', ''),
                    "thumbnail_url": channel_info.get('thumbnail_url', ''),
                    "subscriber_count": channel_info.get('subscriber_count', 0),
                    "video_count": channel_info.get('video_count', 0),
                    "view_count": channel_info.get('view_count', 0),
                    "subscriber_count_hidden": channel_info.get('subscriber_count_hidden', False),
                    "privacy_status": channel_info.get('privacy_status', ''),
                    "is_linked": channel_info.get('is_linked', False),
                    "long_uploads_status": channel_info.get('long_uploads_status', ''),
                    "made_for_kids": channel_info.get('made_for_kids', False),
                    "self_declared_made_for_kids": channel_info.get('self_declared_made_for_kids', False),
                    "topic_ids": channel_info.get('topic_ids', []),
                    "topic_categories": channel_info.get('topic_categories', []),
                    "keywords": channel_info.get('keywords', ''),
                    "channel_url": channel_info.get('channel_url', f"https://www.youtube.com/channel/{channel_id}" if channel_id != 'N/A' else '')
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
            print(f"   \n📺 频道信息:")
            print(f"   频道名称: {video_data['channel_info']['title']}")
            print(f"   订阅者数: {video_data['channel_info']['subscriber_count']:,}")
            print(f"   频道国家: {video_data['channel_info']['country'] or '未知'}")
            print(f"   频道视频总数: {video_data['channel_info']['video_count']:,}")
            print(f"   频道总观看数: {video_data['channel_info']['view_count']:,}")
            print(f"   频道创建时间: {video_data['channel_info']['published_at'] or '未知'}")
            if video_data['channel_info']['custom_url']:
                print(f"   频道自定义URL: {video_data['channel_info']['custom_url']}")
            if video_data['channel_info']['topic_categories']:
                print(f"   频道主题: {', '.join(video_data['channel_info']['topic_categories'][:3])}")
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
    """主函数 - 支持命令行参数和环境变量，支持搜索、评论获取和频道视频获取三种模式"""
    
    # 从环境变量获取配置
    api_key = os.getenv('YOUTUBE_API_KEY')
    mode = os.getenv('MODE', 'search')  # 默认为搜索模式
    
    # 搜索模式参数
    search_query = os.getenv('SEARCH_QUERY')
    max_results = int(os.getenv('MAX_RESULTS', '25'))
    published_after = os.getenv('PUBLISHED_AFTER')  # 时间筛选：之后
    published_before = os.getenv('PUBLISHED_BEFORE')  # 时间筛选：之前
    
    # 评论模式参数
    video_id = os.getenv('VIDEO_ID')
    max_comments = int(os.getenv('MAX_COMMENTS', '50'))
    
    # 频道模式参数
    channel_handle = os.getenv('CHANNEL_HANDLE')
    max_videos = int(os.getenv('MAX_VIDEOS', '50'))
    batch_size = int(os.getenv('BATCH_SIZE', '100'))  # 分批大小，默认100
    
    # 通用参数
    webhook_url = os.getenv('WEBHOOK_URL')
    
    # 命令行参数优先级更高
    if len(sys.argv) > 1:
        mode = sys.argv[1]  # 第一个参数是模式
    if len(sys.argv) > 2:
        if mode == 'search':
            search_query = sys.argv[2]
        elif mode == 'comments':
            video_id = sys.argv[2]
        elif mode == 'channel':
            channel_handle = sys.argv[2]
    if len(sys.argv) > 3:
        if mode == 'search':
            max_results = int(sys.argv[3])
        elif mode == 'comments':
            max_comments = int(sys.argv[3])
        elif mode == 'channel':
            max_videos = int(sys.argv[3])
    if len(sys.argv) > 4:
        api_key = sys.argv[4]  # API密钥作为第4个参数
    if len(sys.argv) > 5:
        webhook_url = sys.argv[5]  # webhook_url作为第5个参数
    if len(sys.argv) > 6 and mode == 'search':
        published_after = sys.argv[6]  # 搜索模式的时间筛选：之后
    if len(sys.argv) > 7 and mode == 'search':
        published_before = sys.argv[7]  # 搜索模式的时间筛选：之前
    
    # 验证必需参数
    if not api_key:
        print("❌ 错误: 未提供YouTube API密钥")
        print("请设置环境变量 YOUTUBE_API_KEY 或作为命令行参数传入")
        sys.exit(1)
    
    # 根据模式验证参数
    if mode == 'search':
        if not search_query:
            print("❌ 错误: 搜索模式下未提供搜索关键词")
            print("请设置环境变量 SEARCH_QUERY 或作为命令行参数传入")
            sys.exit(1)
    elif mode == 'comments':
        if not video_id:
            print("❌ 错误: 评论模式下未提供视频ID")
            print("请设置环境变量 VIDEO_ID 或作为命令行参数传入")
            sys.exit(1)
    elif mode == 'channel':
        if not channel_handle:
            print("❌ 错误: 频道模式下未提供频道Handle")
            print("请设置环境变量 CHANNEL_HANDLE 或作为命令行参数传入")
            sys.exit(1)
    else:
        print("❌ 错误: 不支持的模式，请使用 'search'、'comments' 或 'channel'")
        sys.exit(1)
    
    print("=" * 60)
    if mode == 'search':
        print("🚀 YouTube搜索API - GitHub Webhook版本")
        print("=" * 60)
        print(f"🔑 API密钥: {'已设置' if api_key else '未设置'}")
        print(f"🔍 搜索关键词: {search_query}")
        print(f"📊 最大结果数: {max_results}")
        if published_after:
            print(f"📅 筛选时间范围: {published_after} 之后")
        if published_before:
            print(f"📅 筛选时间范围: {published_before} 之前")
    elif mode == 'comments':
        print("💬 YouTube评论获取API - GitHub Webhook版本")
        print("=" * 60)
        print(f"🔑 API密钥: {'已设置' if api_key else '未设置'}")
        print(f"🎥 视频ID: {video_id}")
        print(f"💬 最大评论数: {max_comments}")
    elif mode == 'channel':
        print("📺 YouTube频道视频获取API - GitHub Webhook版本")
        print("=" * 60)
        print(f"🔑 API密钥: {'已设置' if api_key else '未设置'}")
        print(f"📺 频道Handle: {channel_handle}")
        print(f"🎬 最大视频数: {max_videos}")
        print(f"📦 分批大小: {batch_size} (每批触发一次webhook)")
    
    print(f"📤 Webhook URL: {'已设置' if webhook_url else '未设置'}")
    print("=" * 60)
    
    try:
        if mode == 'search':
            # 执行搜索
            results = search_youtube_videos(
                api_key=api_key,
                search_query=search_query,
                max_results=max_results,
                webhook_url=webhook_url,
                published_after=published_after,
                published_before=published_before
            )
            
            # 输出结果摘要
            if results:
                print(f"\n📋 搜索结果摘要:")
                for i, video in enumerate(results[:5], 1):  # 显示前5个结果
                    basic_info = video.get('basic_info', {})
                    snippet = video.get('snippet', {})
                    stats = video.get('statistics', {})
                    title = snippet.get('title', 'N/A')
                    channel_title = snippet.get('channel_title', 'N/A')
                    print(f"{i}. {title[:60]}...")
                    print(f"   📺 频道: {channel_title}")
                    print(f"   👀 观看: {stats.get('view_count', 0):,} | 👍 点赞: {stats.get('like_count', 0):,}")
                    print(f"   🔗 链接: {basic_info.get('video_url', 'N/A')}")
                    print()
            
            # 如果没有webhook，将结果保存到文件
            if not webhook_url:
                output_file = f"youtube_search_results_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 结果已保存到: {output_file}")
        
        elif mode == 'comments':
            # 执行评论获取
            results = get_video_comments(
                api_key=api_key,
                video_id=video_id,
                max_comments=max_comments,
                webhook_url=webhook_url
            )
            
            # 输出结果摘要
            if results and 'comments' in results and len(results['comments']) > 0:
                video_info = results['video_info']
                comments = results['comments']
                print(f"\n📋 评论获取结果摘要:")
                if 'title' in video_info and 'channel_title' in video_info:
                    print(f"🎥 视频: {video_info['title'][:60]}...")
                    print(f"📺 频道: {video_info['channel_title']}")
                print(f"💬 获取到 {len(comments)} 条评论")
                if comments:
                    print(f"\n🔥 热门评论预览:")
                    for i, comment in enumerate(comments[:3], 1):  # 显示前3条评论
                        print(f"{i}. 👤 {comment['author_name']}")
                        print(f"   💬 {comment['text'][:100]}...")
                        print(f"   👍 {comment['like_count']:,} 赞 | 📅 {comment['published_at']}")
                        print()
            elif results and 'error' in results:
                print(f"\n❌ 获取评论失败: {results.get('error', '未知错误')}")
            else:
                print(f"\n❌ 未能获取到评论数据")
            
            # 如果没有webhook，将结果保存到文件
            if not webhook_url:
                output_file = f"youtube_comments_{video_id}_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 结果已保存到: {output_file}")
        
        elif mode == 'channel':
            # 执行频道视频获取
            results = get_channel_videos(
                api_key=api_key,
                handle=channel_handle,
                max_results=max_videos,
                webhook_url=webhook_url,
                batch_size=batch_size
            )
            
            # 输出结果摘要
            if results and 'videos' in results and len(results['videos']) > 0:
                channel_info = results['channel_info']
                videos = results['videos']
                print(f"\n📋 频道视频获取结果摘要:")
                print(f"📺 频道: {channel_info['title'][:60]}...")
                print(f"👥 订阅者: {channel_info['subscriber_count']:,} | 🎬 总视频: {channel_info['video_count']:,}")
                print(f"📊 获取到 {len(videos)} 个视频")
                if videos:
                    print(f"\n🔥 热门视频预览:")
                    for i, video in enumerate(videos[:5], 1):  # 显示前5个视频
                        print(f"{i}. 🎥 {video['title'][:60]}...")
                        print(f"   👀 观看: {video['view_count']:,} | 👍 点赞: {video['like_count']:,}")
                        print(f"   📅 发布: {video['published_at']} | 🔗 {video['video_url']}")
                        print()
            elif results and 'error' in results:
                print(f"\n❌ 获取频道视频失败: {results.get('error', '未知错误')}")
            else:
                print(f"\n❌ 未能获取到频道视频数据")
            
            # 如果没有webhook，将结果保存到文件
            if not webhook_url:
                # 生成安全的文件名，移除特殊字符
                safe_handle = channel_handle.replace('https://www.youtube.com/', '').replace('/', '_').replace(':', '_')
                output_file = f"youtube_channel_{safe_handle}_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 结果已保存到: {output_file}")
        
        print("\n🎉 任务完成！")
        
    except Exception as e:
        print(f"\n💥 任务失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()