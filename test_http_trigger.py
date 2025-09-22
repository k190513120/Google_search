#!/usr/bin/env python3
"""
测试HTTP触发GitHub Actions功能
"""

import requests
import json
import os
import time

def test_github_api_trigger():
    """测试GitHub API触发功能"""
    
    # 配置参数
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'ghp_test_token')  # 请设置实际的token
    REPO_OWNER = "k190513120"
    REPO_NAME = "Google_search"
    
    # API端点
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    
    # 请求头
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # 测试载荷 - YouTube搜索带时间筛选
    payload = {
        "event_type": "youtube-search",
        "client_payload": {
            "mode": "search",
            "search_query": "HONOR test",
            "max_results": "3",
            "published_after": "2024-01-01"
        }
    }
    
    print("=" * 60)
    print("🧪 测试GitHub Actions HTTP触发功能")
    print("=" * 60)
    
    print(f"📡 API端点: {url}")
    print(f"🔑 Token状态: {'已设置' if GITHUB_TOKEN != 'ghp_test_token' else '未设置(使用测试值)'}")
    print(f"📋 测试载荷:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    if GITHUB_TOKEN == 'ghp_test_token':
        print("\n⚠️  警告: 请设置实际的GITHUB_TOKEN环境变量")
        print("   export GITHUB_TOKEN='your_actual_token'")
        return False
    
    try:
        print(f"\n🚀 发送HTTP请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Action触发成功！")
            print(f"🔗 查看执行状态: https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
            return True
        elif response.status_code == 401:
            print("❌ 认证失败: Token无效或权限不足")
            print("   请检查GITHUB_TOKEN是否正确设置")
        elif response.status_code == 404:
            print("❌ 仓库未找到: 请检查仓库路径是否正确")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
        
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False

def test_curl_command():
    """生成cURL测试命令"""
    
    REPO_OWNER = "k190513120"
    REPO_NAME = "Google_search"
    
    curl_command = f'''curl -X POST \\
  -H "Authorization: token YOUR_GITHUB_TOKEN" \\
  -H "Accept: application/vnd.github.v3+json" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "event_type": "youtube-search",
    "client_payload": {{
      "mode": "search",
      "search_query": "HONOR test",
      "max_results": "3",
      "published_after": "2024-01-01"
    }}
  }}' \\
  https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches'''
    
    print("\n" + "=" * 60)
    print("📋 等效的cURL命令:")
    print("=" * 60)
    print(curl_command)
    print("\n💡 使用方法: 将YOUR_GITHUB_TOKEN替换为实际的token值")

if __name__ == "__main__":
    # 测试Python API调用
    success = test_github_api_trigger()
    
    # 显示cURL命令示例
    test_curl_command()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试完成！Action已成功触发")
    else:
        print("⚠️  测试未完全成功，请检查配置")
    print("=" * 60)