#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：使用分页搜索获取更多YouTube视频结果

这个示例展示了如何使用改进后的搜索功能来获取超过50条的搜索结果，
同时优化API配额的使用。
"""

import os
import sys
from youtube_search_webhook import search_youtube_videos

def main():
    # 设置API密钥
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 请设置环境变量 YOUTUBE_API_KEY")
        return
    
    # 搜索参数
    search_query = "Python编程教程"
    
    # 测试不同的结果数量
    test_cases = [
        {"max_results": 25, "description": "获取25条结果（单次请求）"},
        {"max_results": 75, "description": "获取75条结果（需要2次搜索请求）"},
        {"max_results": 150, "description": "获取150条结果（需要3次搜索请求）"},
    ]
    
    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 测试案例: {case['description']}")
        print(f"{'='*60}")
        
        try:
            results = search_youtube_videos(
                api_key=api_key,
                search_query=search_query,
                max_results=case['max_results']
            )
            
            print(f"\n📊 搜索结果统计:")
            print(f"   - 请求的结果数: {case['max_results']}")
            print(f"   - 实际获取数: {len(results)}")
            
            if results:
                print(f"\n📋 前5个视频预览:")
                for i, video in enumerate(results[:5], 1):
                    title = video.get('basic_info', {}).get('title', 'N/A')
                    view_count = video.get('statistics', {}).get('view_count', 'N/A')
                    print(f"   {i}. {title[:50]}... (观看数: {view_count})")
            
        except Exception as e:
            print(f"❌ 搜索失败: {str(e)}")
        
        print(f"\n{'='*60}")
        input("按回车键继续下一个测试...")

def demo_quota_optimization():
    """演示配额优化策略"""
    print("\n🎯 配额优化策略演示")
    print("="*50)
    
    scenarios = [
        {"results": 25, "quota": "100 + 1 = 101 单位"},
        {"results": 50, "quota": "100 + 1 = 101 单位"},
        {"results": 75, "quota": "200 + 2 = 202 单位"},
        {"results": 100, "quota": "200 + 2 = 202 单位"},
        {"results": 150, "quota": "300 + 3 = 303 单位"},
    ]
    
    print("📊 不同结果数量的配额消耗:")
    for scenario in scenarios:
        print(f"   - {scenario['results']:3d} 条结果: {scenario['quota']}")
    
    print("\n💡 优化建议:")
    print("   1. 根据实际需求设置 max_results，避免过度获取")
    print("   2. 每50条结果需要1次搜索请求（100配额）+ 1次视频详情请求（1配额）")
    print("   3. 如果搜索结果不足，会自动停止，节省配额")
    print("   4. 建议批量处理，减少API调用频率")

if __name__ == "__main__":
    print("🚀 YouTube搜索分页功能测试")
    print("="*50)
    
    # 检查API密钥
    if not os.getenv('YOUTUBE_API_KEY'):
        print("❌ 请先设置环境变量 YOUTUBE_API_KEY")
        print("   export YOUTUBE_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    # 显示配额优化信息
    demo_quota_optimization()
    
    # 询问是否继续测试
    response = input("\n是否继续进行实际搜索测试？(y/N): ")
    if response.lower() in ['y', 'yes', '是']:
        main()
    else:
        print("👋 测试结束")