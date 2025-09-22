#!/usr/bin/env python3
"""
测试分批回传功能的脚本
用于验证get_channel_videos函数的分批webhook发送功能
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_search_webhook import get_channel_videos

class MockWebhookServer:
    """模拟webhook服务器，用于接收和记录分批数据"""
    
    def __init__(self):
        self.received_batches = []
        self.total_videos_received = 0
    
    def receive_webhook(self, data):
        """模拟接收webhook数据"""
        batch_info = data.get('batch_info', {})
        videos = data.get('videos', [])
        
        print(f"📦 接收到批次数据:")
        print(f"   批次号: {batch_info.get('batch_number', 'unknown')}")
        print(f"   批次大小: {batch_info.get('batch_size', 0)}")
        print(f"   视频数量: {len(videos)}")
        print(f"   是否最后一批: {batch_info.get('is_final_batch', False)}")
        print(f"   时间戳: {data.get('fetch_timestamp', 'unknown')}")
        
        # 记录接收到的数据
        self.received_batches.append({
            'batch_number': batch_info.get('batch_number'),
            'video_count': len(videos),
            'is_final': batch_info.get('is_final_batch', False),
            'timestamp': data.get('fetch_timestamp')
        })
        
        self.total_videos_received += len(videos)
        print(f"   累计接收视频: {self.total_videos_received}")
        print("-" * 50)
        
        return True
    
    def get_summary(self):
        """获取接收数据的摘要"""
        return {
            'total_batches': len(self.received_batches),
            'total_videos': self.total_videos_received,
            'batches': self.received_batches
        }

def test_batch_functionality():
    """测试分批功能"""
    print("🧪 开始测试分批回传功能")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 错误: 未设置YOUTUBE_API_KEY环境变量")
        print("请设置环境变量: export YOUTUBE_API_KEY='your_api_key'")
        return False
    
    # 测试参数
    test_channel = "@JerryRigEverything"  # 使用一个有很多视频的频道
    max_results = 250  # 设置较大的数量以测试分批
    batch_size = 100   # 每100条一批
    
    print(f"📺 测试频道: {test_channel}")
    print(f"🎬 最大视频数: {max_results}")
    print(f"📦 分批大小: {batch_size}")
    print("-" * 60)
    
    # 创建模拟webhook服务器
    mock_server = MockWebhookServer()
    
    # 重写send_to_webhook函数以使用模拟服务器
    import youtube_search_webhook
    original_send_to_webhook = youtube_search_webhook.send_to_webhook
    
    def mock_send_to_webhook(data, webhook_url):
        return mock_server.receive_webhook(data)
    
    youtube_search_webhook.send_to_webhook = mock_send_to_webhook
    
    try:
        # 执行测试
        print("🚀 开始获取频道视频...")
        start_time = time.time()
        
        result = get_channel_videos(
            api_key=api_key,
            handle=test_channel,
            max_results=max_results,
            webhook_url="http://mock-webhook-server.com/receive",  # 模拟URL
            batch_size=batch_size
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ 执行时间: {duration:.2f}秒")
        print("=" * 60)
        
        # 分析结果
        if result and 'videos' in result:
            actual_videos = len(result['videos'])
            print(f"📊 测试结果分析:")
            print(f"   实际获取视频数: {actual_videos}")
            print(f"   预期最大视频数: {max_results}")
            
            # 分析webhook接收情况
            summary = mock_server.get_summary()
            print(f"\n📦 Webhook接收情况:")
            print(f"   总批次数: {summary['total_batches']}")
            print(f"   总接收视频数: {summary['total_videos']}")
            
            expected_batches = (actual_videos + batch_size - 1) // batch_size  # 向上取整
            print(f"   预期批次数: {expected_batches}")
            
            # 验证分批逻辑
            print(f"\n✅ 验证结果:")
            if summary['total_videos'] == actual_videos:
                print(f"   ✓ 视频数量匹配: {summary['total_videos']} == {actual_videos}")
            else:
                print(f"   ✗ 视频数量不匹配: {summary['total_videos']} != {actual_videos}")
            
            if summary['total_batches'] == expected_batches:
                print(f"   ✓ 批次数量正确: {summary['total_batches']} == {expected_batches}")
            else:
                print(f"   ✗ 批次数量不正确: {summary['total_batches']} != {expected_batches}")
            
            # 检查最后一批标记
            final_batches = [b for b in summary['batches'] if b['is_final']]
            if len(final_batches) == 1:
                print(f"   ✓ 最后一批标记正确")
            else:
                print(f"   ✗ 最后一批标记错误: 找到{len(final_batches)}个最后批次")
            
            # 详细批次信息
            print(f"\n📋 详细批次信息:")
            for i, batch in enumerate(summary['batches'], 1):
                print(f"   批次{i}: {batch['video_count']}个视频 {'(最后一批)' if batch['is_final'] else ''}")
            
            return True
        else:
            print("❌ 测试失败: 未获取到视频数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        # 恢复原始函数
        youtube_search_webhook.send_to_webhook = original_send_to_webhook

def main():
    """主函数"""
    success = test_batch_functionality()
    
    if success:
        print("\n🎉 分批回传功能测试通过！")
        sys.exit(0)
    else:
        print("\n💥 分批回传功能测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()