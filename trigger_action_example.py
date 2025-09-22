#!/usr/bin/env python3
"""
GitHub Actions HTTP调用示例脚本
通过repository_dispatch事件触发YouTube搜索Action
"""

import requests
import json
import os
from datetime import datetime

class GitHubActionTrigger:
    def __init__(self, github_token, repo_owner, repo_name):
        """
        初始化GitHub Action触发器
        
        Args:
            github_token: GitHub Personal Access Token
            repo_owner: 仓库所有者
            repo_name: 仓库名称
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
        
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def trigger_youtube_search(self, search_query, max_results=25, webhook_url=None, 
                             published_after=None, published_before=None):
        """
        触发YouTube搜索Action
        
        Args:
            search_query: 搜索关键词
            max_results: 最大结果数量
            webhook_url: Webhook URL (可选)
            published_after: 筛选时间范围：之后 (格式: YYYY-MM-DD)
            published_before: 筛选时间范围：之前 (格式: YYYY-MM-DD)
        """
        payload = {
            "event_type": "youtube-search",
            "client_payload": {
                "mode": "search",
                "search_query": search_query,
                "max_results": str(max_results)
            }
        }
        
        # 添加可选参数
        if webhook_url:
            payload["client_payload"]["webhook_url"] = webhook_url
        if published_after:
            payload["client_payload"]["published_after"] = published_after
        if published_before:
            payload["client_payload"]["published_before"] = published_before
        
        return self._send_request(payload)
    
    def trigger_youtube_comments(self, video_id, max_comments=50, webhook_url=None):
        """
        触发YouTube评论获取Action
        
        Args:
            video_id: YouTube视频ID
            max_comments: 最大评论数量
            webhook_url: Webhook URL (可选)
        """
        payload = {
            "event_type": "youtube-comments",
            "client_payload": {
                "mode": "comments",
                "video_id": video_id,
                "max_comments": str(max_comments)
            }
        }
        
        if webhook_url:
            payload["client_payload"]["webhook_url"] = webhook_url
        
        return self._send_request(payload)
    
    def trigger_youtube_channel(self, channel_handle, max_videos=50, webhook_url=None):
        """
        触发YouTube频道视频获取Action
        
        Args:
            channel_handle: 频道Handle (如@JerryRigEverything)
            max_videos: 最大视频数量
            webhook_url: Webhook URL (可选)
        """
        payload = {
            "event_type": "youtube-channel",
            "client_payload": {
                "mode": "channel",
                "channel_handle": channel_handle,
                "max_videos": str(max_videos)
            }
        }
        
        if webhook_url:
            payload["client_payload"]["webhook_url"] = webhook_url
        
        return self._send_request(payload)
    
    def _send_request(self, payload):
        """发送HTTP请求到GitHub API"""
        try:
            print(f"🚀 发送请求到GitHub Actions...")
            print(f"📋 请求载荷: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 204:
                print(f"✅ Action触发成功！")
                print(f"🔗 查看执行状态: https://github.com/{self.repo_owner}/{self.repo_name}/actions")
                return True
            else:
                print(f"❌ Action触发失败: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 请求发送失败: {str(e)}")
            return False

def main():
    """主函数 - 示例用法"""
    
    # 配置参数 (请替换为实际值)
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your_github_token_here')
    REPO_OWNER = "k190513120"  # 替换为你的GitHub用户名
    REPO_NAME = "Google_search"  # 替换为你的仓库名
    
    # 创建触发器实例
    trigger = GitHubActionTrigger(GITHUB_TOKEN, REPO_OWNER, REPO_NAME)
    
    print("=" * 60)
    print("🎯 GitHub Actions HTTP调用示例")
    print("=" * 60)
    
    # 示例1: 搜索带时间筛选的视频
    print("\n📱 示例1: 搜索2024年发布的HONOR相关视频")
    success = trigger.trigger_youtube_search(
        search_query="HONOR",
        max_results=10,
        published_after="2024-01-01",
        published_before="2024-12-31"
    )
    
    if success:
        print("✅ 搜索任务已提交")
    else:
        print("❌ 搜索任务提交失败")
    
    # 示例2: 获取视频评论
    print("\n💬 示例2: 获取视频评论")
    success = trigger.trigger_youtube_comments(
        video_id="dQw4w9WgXcQ",  # 示例视频ID
        max_comments=20
    )
    
    if success:
        print("✅ 评论获取任务已提交")
    else:
        print("❌ 评论获取任务提交失败")
    
    # 示例3: 获取频道视频
    print("\n📺 示例3: 获取频道视频")
    success = trigger.trigger_youtube_channel(
        channel_handle="@JerryRigEverything",
        max_videos=15
    )
    
    if success:
        print("✅ 频道视频获取任务已提交")
    else:
        print("❌ 频道视频获取任务提交失败")

if __name__ == "__main__":
    main()