# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import googleapiclient.discovery
import googleapiclient.errors
import httplib2
import socket
import socks
import requests
import json
import time

def send_to_webhook(video_data, webhook_url):
    """发送视频数据到webhook"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'YouTube-Search-Bot/1.0'
        }
        
        response = requests.post(
            webhook_url, 
            json=video_data, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Webhook发送成功: {response.status_code}")
            return True
        else:
            print(f"   ❌ Webhook发送失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Webhook发送异常: {e}")
        return False

def main():
    # API information
    api_service_name = "youtube"
    api_version = "v3"
    # API key provided by the user
    DEVELOPER_KEY = "AIzaSyCaj6T2qTsSTjYom9rYUXFtRAO0-EdtnSA"
    
    # Webhook配置
    WEBHOOK_URL = "https://larkcommunity.feishu.cn/base/workflow/webhook/event/WIjjav04EwNkyJhVr4ncBZorn4d"
    SEND_TO_WEBHOOK = True  # 设置为True启用webhook发送，False禁用
    
    # 代理配置 - 请根据您的代理设置修改以下参数
    USE_PROXY = True  # 设置为True启用代理，False禁用代理
    PROXY_HOST = "127.0.0.1"  # 代理服务器地址
    PROXY_PORT = 7890  # 代理服务器端口
    PROXY_TYPE = "HTTP"  # 代理类型: "HTTP", "SOCKS4", "SOCKS5"

    # Create a YouTube API client with custom HTTP settings
    try:
        # Create HTTP object with timeout and proxy settings
        if USE_PROXY:
            print(f"使用代理: {PROXY_TYPE}://{PROXY_HOST}:{PROXY_PORT}")
            
            # 根据代理类型设置
            if PROXY_TYPE.upper() == "HTTP":
                proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_HTTP,
                    PROXY_HOST,
                    PROXY_PORT
                )
            elif PROXY_TYPE.upper() == "SOCKS4":
                proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_SOCKS4,
                    PROXY_HOST,
                    PROXY_PORT
                )
            elif PROXY_TYPE.upper() == "SOCKS5":
                proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_SOCKS5,
                    PROXY_HOST,
                    PROXY_PORT
                )
            else:
                print(f"不支持的代理类型: {PROXY_TYPE}，使用直连")
                proxy_info = None
                
            http = httplib2.Http(proxy_info=proxy_info, timeout=30)
        else:
            print("使用直连（无代理）")
            http = httplib2.Http(timeout=30)
        
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY, http=http)

        # Build the request
        request = youtube.search().list(
            part="snippet",
            q="HONOR 400",  # The search term
            maxResults=25,
            order="viewCount"
        )
    
        # Execute the request
        print("正在发送请求到YouTube API...")
        response = request.execute()
        print("请求成功！")
        print("\n=== YouTube搜索结果 ===")
        
        # 收集视频ID以获取详细统计信息
        video_ids = []
        for item in response.get('items', []):
            video_id = item.get('id', {}).get('videoId')
            if video_id:
                video_ids.append(video_id)
        
        # 获取视频详细信息（包括统计数据）
        video_details = {}
        if video_ids:
            print("正在获取视频详细统计信息...")
            try:
                videos_request = youtube.videos().list(
                    part="statistics,contentDetails,status",
                    id=','.join(video_ids[:15])  # 限制为前15个视频
                )
                videos_response = videos_request.execute()
                
                for video in videos_response.get('items', []):
                    video_id = video.get('id')
                    if video_id:
                        video_details[video_id] = {
                            'statistics': video.get('statistics', {}),
                            'contentDetails': video.get('contentDetails', {}),
                            'status': video.get('status', {})
                        }
                print("统计信息获取成功！")
            except Exception as e:
                print(f"获取统计信息时出错: {e}")
        
        # 获取视频评论信息
        video_comments = {}
        if video_ids:
            print("正在获取视频评论信息...")
            for video_id in video_ids[:15]:  # 限制为前15个视频
                try:
                    comments_request = youtube.commentThreads().list(
                        part="snippet,replies",
                        videoId=video_id,
                        maxResults=10,  # 每个视频获取最多10条评论
                        order="relevance"  # 按相关性排序
                    )
                    comments_response = comments_request.execute()
                    
                    comments_list = []
                    for comment_thread in comments_response.get('items', []):
                        thread_snippet = comment_thread.get('snippet', {})
                        top_comment = thread_snippet.get('topLevelComment', {}).get('snippet', {})
                        
                        comment_data = {
                            'comment_id': comment_thread.get('id', ''),
                            'author': top_comment.get('authorDisplayName', ''),
                            'author_channel_id': top_comment.get('authorChannelId', {}).get('value', ''),
                            'text': top_comment.get('textDisplay', ''),
                            'like_count': top_comment.get('likeCount', 0),
                            'published_at': top_comment.get('publishedAt', ''),
                            'updated_at': top_comment.get('updatedAt', ''),
                            'reply_count': thread_snippet.get('totalReplyCount', 0),
                            'can_reply': thread_snippet.get('canReply', False)
                        }
                        
                        # 获取回复评论（如果有）
                        replies = []
                        if 'replies' in comment_thread:
                            for reply in comment_thread['replies'].get('comments', []):
                                reply_snippet = reply.get('snippet', {})
                                reply_data = {
                                    'reply_id': reply.get('id', ''),
                                    'author': reply_snippet.get('authorDisplayName', ''),
                                    'author_channel_id': reply_snippet.get('authorChannelId', {}).get('value', ''),
                                    'text': reply_snippet.get('textDisplay', ''),
                                    'like_count': reply_snippet.get('likeCount', 0),
                                    'published_at': reply_snippet.get('publishedAt', ''),
                                    'updated_at': reply_snippet.get('updatedAt', '')
                                }
                                replies.append(reply_data)
                        
                        comment_data['replies'] = replies
                        comments_list.append(comment_data)
                    
                    video_comments[video_id] = comments_list
                    print(f"   ✅ 视频 {video_id} 评论获取成功: {len(comments_list)} 条评论")
                    
                    # 添加延迟避免API限制
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ❌ 获取视频 {video_id} 评论时出错: {e}")
                    video_comments[video_id] = []
            
            print("评论信息获取完成！")
        
        # 解析并显示结果
        if 'items' in response:
            print(f"\n总结果数: {response.get('pageInfo', {}).get('totalResults', 'N/A')}")
            print(f"当前页结果数: {response.get('pageInfo', {}).get('resultsPerPage', 'N/A')}")
            print(f"区域代码: {response.get('regionCode', 'N/A')}")
            if 'nextPageToken' in response:
                print(f"下一页Token: {response['nextPageToken']}")
            
            for i, item in enumerate(response['items'][:15], 1):  # 显示前15个结果
                # 基本信息
                kind = item.get('kind', 'N/A')
                etag = item.get('etag', 'N/A')
                
                # ID信息
                id_info = item.get('id', {})
                id_kind = id_info.get('kind', 'N/A')
                video_id = id_info.get('videoId', 'N/A')
                
                # Snippet信息
                snippet = item.get('snippet', {})
                title = snippet.get('title', 'N/A')
                channel = snippet.get('channelTitle', 'N/A')
                channel_id = snippet.get('channelId', 'N/A')
                published_at = snippet.get('publishedAt', 'N/A')
                publish_time = snippet.get('publishTime', 'N/A')
                description = snippet.get('description', '')
                live_broadcast = snippet.get('liveBroadcastContent', 'N/A')
                
                # 缩略图信息
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_default = thumbnails.get('default', {}).get('url', 'N/A')
                thumbnail_medium = thumbnails.get('medium', {}).get('url', 'N/A')
                thumbnail_high = thumbnails.get('high', {}).get('url', 'N/A')
                
                # 生成视频链接
                video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id != 'N/A' else 'N/A'
                
                # 格式化描述
                desc_preview = description[:100] + "..." if len(description) > 100 else description
                
                # 获取视频统计信息
                stats = video_details.get(video_id, {}).get('statistics', {})
                content_details = video_details.get(video_id, {}).get('contentDetails', {})
                status = video_details.get(video_id, {}).get('status', {})
                
                # 统计数据
                view_count = stats.get('viewCount', 'N/A')
                like_count = stats.get('likeCount', 'N/A')
                comment_count = stats.get('commentCount', 'N/A')
                favorite_count = stats.get('favoriteCount', 'N/A')
                
                # 获取评论数据
                comments_data = video_comments.get(video_id, [])
                comments_summary = f"{len(comments_data)} 条评论已获取" if comments_data else "无评论数据"
                
                # 内容详情
                duration = content_details.get('duration', 'N/A')
                definition = content_details.get('definition', 'N/A')
                caption = content_details.get('caption', 'N/A')
                licensed_content = content_details.get('licensedContent', 'N/A')
                
                # 状态信息
                upload_status = status.get('uploadStatus', 'N/A')
                privacy_status = status.get('privacyStatus', 'N/A')
                license_type = status.get('license', 'N/A')
                embeddable = status.get('embeddable', 'N/A')
                public_stats_viewable = status.get('publicStatsViewable', 'N/A')
                
                print(f"\n{'='*60}")
                print(f"{i}. 【{title}】")
                print(f"   Kind: {kind}")
                print(f"   ID Kind: {id_kind}")
                print(f"   视频ID: {video_id}")
                print(f"   视频链接: {video_url}")
                print(f"   频道: {channel}")
                print(f"   频道ID: {channel_id}")
                print(f"   发布时间: {published_at}")
                print(f"   发布时间(本地): {publish_time}")
                print(f"   直播状态: {live_broadcast}")
                print(f"   \n📊 统计数据:")
                print(f"   观看次数: {view_count}")
                print(f"   点赞数: {like_count}")
                print(f"   评论数: {comment_count}")
                print(f"   收藏数: {favorite_count}")
                print(f"   获取的评论: {comments_summary}")
                print(f"   \n🎬 内容详情:")
                print(f"   视频时长: {duration}")
                print(f"   视频清晰度: {definition}")
                print(f"   字幕: {caption}")
                print(f"   授权内容: {licensed_content}")
                print(f"   \n🔒 状态信息:")
                print(f"   上传状态: {upload_status}")
                print(f"   隐私状态: {privacy_status}")
                print(f"   许可类型: {license_type}")
                print(f"   可嵌入: {embeddable}")
                print(f"   公开统计: {public_stats_viewable}")
                print(f"   \n📝 描述信息:")
                print(f"   描述预览: {desc_preview}")
                print(f"   完整描述: {description}")
                print(f"   \n🖼️ 缩略图:")
                print(f"   缩略图(默认): {thumbnail_default}")
                print(f"   缩略图(中等): {thumbnail_medium}")
                print(f"   缩略图(高清): {thumbnail_high}")
                print(f"   \n🏷️ 元数据:")
                print(f"   ETag: {etag}")
                
                # 显示评论详情
                if comments_data:
                    print(f"   \n💬 评论详情 (显示前5条):")
                    for idx, comment in enumerate(comments_data[:5], 1):
                        comment_text = comment['text'][:100] + "..." if len(comment['text']) > 100 else comment['text']
                        print(f"   {idx}. 【{comment['author']}】: {comment_text}")
                        print(f"      👍 {comment['like_count']} | 📅 {comment['published_at'][:10]} | 💬 {comment['reply_count']} 回复")
                        if comment['replies']:
                            for reply_idx, reply in enumerate(comment['replies'][:2], 1):  # 显示前2个回复
                                reply_text = reply['text'][:80] + "..." if len(reply['text']) > 80 else reply['text']
                                print(f"        └─ 回复{reply_idx}: 【{reply['author']}】: {reply_text}")
                else:
                    print(f"   \n💬 评论详情: 暂无评论数据")
                
                # 发送到Webhook
                if SEND_TO_WEBHOOK:
                    print(f"   \n📤 发送到Webhook...")
                    
                    # 构建发送到webhook的数据结构
                    webhook_data = {
                        "video_info": {
                            "basic_info": {
                                "kind": kind,
                                "id_kind": id_kind,
                                "video_id": video_id,
                                "video_url": video_url,
                                "title": title,
                                "channel": channel,
                                "channel_id": channel_id,
                                "published_at": published_at,
                                "publish_time": publish_time,
                                "live_broadcast_content": live_broadcast,
                                "etag": etag
                            },
                            "statistics": {
                                "view_count": view_count,
                                "like_count": like_count,
                                "comment_count": comment_count,
                                "favorite_count": favorite_count
                            },
                            "content_details": {
                                "duration": duration,
                                "definition": definition,
                                "caption": caption,
                                "licensed_content": licensed_content
                            },
                            "status": {
                                "upload_status": upload_status,
                                "privacy_status": privacy_status,
                                "license": license_type,
                                "embeddable": embeddable,
                                "public_stats_viewable": public_stats_viewable
                            },
                            "description": {
                                "description_preview": desc_preview,
                                "full_description": description
                            },
                            "thumbnails": {
                                "default": thumbnail_default,
                                "medium": thumbnail_medium,
                                "high": thumbnail_high
                            },
                            "comments": {
                                "total_fetched": len(comments_data),
                                "comments_list": comments_data
                            }
                        },
                        "search_metadata": {
                            "search_query": "荣耀手机",
                            "result_index": i,
                            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                    
                    # 发送到webhook
                    send_to_webhook(webhook_data, WEBHOOK_URL)
                    
                    # 添加延迟避免请求过于频繁
                    time.sleep(1)
        else:
            print("没有找到搜索结果")
            
    except googleapiclient.errors.HttpError as e:
        print(f"HTTP错误 {e.resp.status}: {e.content.decode('utf-8')}")
    except socket.timeout:
        print("连接超时。请检查网络连接或尝试使用VPN。")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()