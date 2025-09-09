#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试频道视频分页功能
用于验证get_channel_videos函数是否能正确处理超过50条视频的获取
"""

import os
import sys
from youtube_search_webhook import get_channel_videos

def test_channel_pagination():
    """
    测试频道视频分页功能
    """
    # 测试频道ID
    channel_id = "UCBJycsmduvYEL83R_U4JriQ"
    
    # 从环境变量获取API密钥
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ 错误: 未设置YouTube API密钥")
        print("请设置环境变量: export YOUTUBE_API_KEY='your_api_key_here'")
        print("")
        print("📝 测试说明:")
        print("1. 本测试需要有效的YouTube Data API v3密钥")
        print("2. 测试频道ID: UCBJycsmduvYEL83R_U4JriQ")
        print("3. 将测试获取不同数量的视频:")
        print("   - 25条 (默认)")
        print("   - 75条 (超过50条，需要分页)")
        print("   - 150条 (需要多次分页)")
        print("")
        print("🔧 使用方法:")
        print("export YOUTUBE_API_KEY='your_api_key_here'")
        print("python test_channel_pagination.py")
        return False
    
    print("🚀 开始测试频道视频分页功能")
    print(f"📺 测试频道ID: {channel_id}")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {"max_results": 25, "description": "基础测试 - 25条视频"},
        {"max_results": 75, "description": "分页测试 - 75条视频 (需要2页)"},
        {"max_results": 150, "description": "多页测试 - 150条视频 (需要3页)"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        max_results = test_case["max_results"]
        description = test_case["description"]
        
        print(f"\n🧪 测试 {i}: {description}")
        print("-" * 40)
        
        try:
            result = get_channel_videos(
                api_key=api_key,
                channel_id=channel_id,
                max_results=max_results
            )
            
            if result and 'videos' in result:
                videos = result['videos']
                channel_info = result['channel_info']
                
                print(f"✅ 测试成功!")
                print(f"   📺 频道: {channel_info.get('title', 'N/A')}")
                print(f"   👥 订阅者: {channel_info.get('subscriber_count', 0):,}")
                print(f"   🎬 频道总视频数: {channel_info.get('video_count', 0):,}")
                print(f"   📊 实际获取: {len(videos)} 个视频")
                print(f"   🎯 目标数量: {max_results}")
                
                if len(videos) > 0:
                    print(f"   🔥 最热门视频: {videos[0]['title'][:50]}...")
                    print(f"   👀 观看次数: {videos[0]['view_count']:,}")
                
            else:
                print(f"❌ 测试失败: 未获取到有效结果")
                if result and 'error' in result:
                    print(f"   错误信息: {result['error']}")
                    
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n🎉 所有测试完成!")
    return True

if __name__ == "__main__":
    test_channel_pagination()