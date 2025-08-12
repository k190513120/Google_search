#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub YouTube搜索触发器示例

这个脚本展示如何通过外部系统触发GitHub上的YouTube搜索功能
可以集成到你的应用中，实现自动化的YouTube数据采集
"""

import requests
import json
import time
from datetime import datetime

class GitHubYouTubeSearchTrigger:
    """GitHub YouTube搜索触发器"""
    
    def __init__(self, github_token, github_username, github_repo):
        """
        初始化触发器
        
        Args:
            github_token: GitHub Personal Access Token
            github_username: GitHub用户名
            github_repo: 仓库名称
        """
        self.github_token = github_token
        self.github_username = github_username
        self.github_repo = github_repo
        self.api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/dispatches"
    
    def trigger_search(self, search_query, webhook_url=None, max_results=25):
        """
        触发YouTube搜索
        
        Args:
            search_query: 搜索关键词
            webhook_url: 结果推送地址（可选）
            max_results: 最大结果数量
            
        Returns:
            bool: 是否触发成功
        """
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "event_type": "youtube-search",
            "client_payload": {
                "search_query": search_query,
                "max_results": str(max_results),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # 如果提供了webhook URL，添加到payload中
        if webhook_url:
            payload["client_payload"]["webhook_url"] = webhook_url
        
        try:
            print(f"🚀 触发YouTube搜索: {search_query}")
            print(f"📊 最大结果数: {max_results}")
            print(f"📤 Webhook: {'已设置' if webhook_url else '未设置'}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 204:
                print("✅ 搜索任务触发成功！")
                print(f"🔗 查看执行状态: https://github.com/{self.github_username}/{self.github_repo}/actions")
                return True
            else:
                print(f"❌ 触发失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 触发异常: {e}")
            return False
    
    def batch_search(self, search_queries, webhook_url=None, max_results=25, delay=60):
        """
        批量触发多个搜索任务
        
        Args:
            search_queries: 搜索关键词列表
            webhook_url: 结果推送地址（可选）
            max_results: 每个搜索的最大结果数量
            delay: 搜索间隔时间（秒）
            
        Returns:
            dict: 批量搜索结果统计
        """
        
        results = {
            "total": len(search_queries),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        print(f"🔄 开始批量搜索，共 {len(search_queries)} 个关键词")
        print(f"⏱️ 搜索间隔: {delay} 秒")
        print("=" * 50)
        
        for i, query in enumerate(search_queries, 1):
            print(f"\n[{i}/{len(search_queries)}] 处理关键词: {query}")
            
            success = self.trigger_search(
                search_query=query,
                webhook_url=webhook_url,
                max_results=max_results
            )
            
            result_detail = {
                "query": query,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            
            results["details"].append(result_detail)
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # 如果不是最后一个，等待指定时间
            if i < len(search_queries):
                print(f"⏳ 等待 {delay} 秒后继续...")
                time.sleep(delay)
        
        print("\n" + "=" * 50)
        print(f"📊 批量搜索完成！")
        print(f"✅ 成功: {results['success']} 个")
        print(f"❌ 失败: {results['failed']} 个")
        
        return results

def main():
    """示例用法"""
    
    # 配置信息（请替换为你的实际信息）
    GITHUB_TOKEN = "your_github_personal_access_token_here"
    GITHUB_USERNAME = "your_github_username"
    GITHUB_REPO = "your_repo_name"
    WEBHOOK_URL = "https://larkcommunity.feishu.cn/base/workflow/webhook/event/your_webhook_id"
    
    # 检查配置
    if "your_" in GITHUB_TOKEN or "your_" in GITHUB_USERNAME:
        print("❌ 请先配置GitHub信息！")
        print("请修改脚本中的以下变量：")
        print("- GITHUB_TOKEN: GitHub Personal Access Token")
        print("- GITHUB_USERNAME: GitHub用户名")
        print("- GITHUB_REPO: 仓库名称")
        print("- WEBHOOK_URL: Webhook地址（可选）")
        return
    
    # 创建触发器实例
    trigger = GitHubYouTubeSearchTrigger(
        github_token=GITHUB_TOKEN,
        github_username=GITHUB_USERNAME,
        github_repo=GITHUB_REPO
    )
    
    print("🎯 GitHub YouTube搜索触发器示例")
    print("=" * 40)
    
    # 示例1：单个搜索
    print("\n📍 示例1：单个关键词搜索")
    trigger.trigger_search(
        search_query="HONOR 400",
        webhook_url=WEBHOOK_URL,
        max_results=25
    )
    
    # 等待一段时间
    print("\n⏳ 等待60秒后执行批量搜索...")
    time.sleep(60)
    
    # 示例2：批量搜索
    print("\n📍 示例2：批量关键词搜索")
    search_keywords = [
        "HONOR 400 review",
        "HONOR 400 unboxing",
        "HONOR 400 vs iPhone",
        "HONOR 400 camera test"
    ]
    
    batch_results = trigger.batch_search(
        search_queries=search_keywords,
        webhook_url=WEBHOOK_URL,
        max_results=15,
        delay=90  # 90秒间隔，避免触发GitHub API限制
    )
    
    # 输出批量结果详情
    print("\n📋 批量搜索详细结果:")
    for detail in batch_results["details"]:
        status = "✅" if detail["success"] else "❌"
        print(f"{status} {detail['query']} - {detail['timestamp'][:19]}")

if __name__ == "__main__":
    main()