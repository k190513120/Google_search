#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub YouTube搜索部署设置脚本

这个脚本帮助用户快速设置和测试GitHub上的YouTube搜索功能
包括配置检查、测试触发和部署验证
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

class DeploymentSetup:
    """部署设置助手"""
    
    def __init__(self):
        self.config = {}
        self.required_files = [
            'youtube_search_webhook.py',
            '.github/workflows/youtube-search.yml',
            'requirements.txt'
        ]
    
    def check_files(self):
        """检查必需文件是否存在"""
        print("📁 检查项目文件...")
        missing_files = []
        
        for file_path in self.required_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - 文件缺失")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️ 缺失 {len(missing_files)} 个必需文件，请确保所有文件都已创建")
            return False
        else:
            print("\n✅ 所有必需文件检查通过！")
            return True
    
    def collect_config(self):
        """收集配置信息"""
        print("\n🔧 配置信息收集")
        print("=" * 30)
        
        # GitHub配置
        print("\n📋 GitHub配置:")
        self.config['github_username'] = input("GitHub用户名: ").strip()
        self.config['github_repo'] = input("仓库名称: ").strip()
        self.config['github_token'] = input("GitHub Personal Access Token: ").strip()
        
        # YouTube API配置
        print("\n📋 YouTube API配置:")
        self.config['youtube_api_key'] = input("YouTube API密钥: ").strip()
        
        # Webhook配置（可选）
        print("\n📋 Webhook配置 (可选):")
        webhook_url = input("飞书多维表格Webhook URL (回车跳过): ").strip()
        if webhook_url:
            self.config['webhook_url'] = webhook_url
        
        # 验证必需配置
        required_configs = ['github_username', 'github_repo', 'github_token', 'youtube_api_key']
        missing_configs = [key for key in required_configs if not self.config.get(key)]
        
        if missing_configs:
            print(f"\n❌ 缺少必需配置: {', '.join(missing_configs)}")
            return False
        
        print("\n✅ 配置信息收集完成！")
        return True
    
    def save_config(self):
        """保存配置到文件"""
        config_file = 'deployment_config.json'
        
        # 不保存敏感信息到文件，只保存非敏感配置
        safe_config = {
            'github_username': self.config['github_username'],
            'github_repo': self.config['github_repo'],
            'webhook_url': self.config.get('webhook_url', ''),
            'setup_date': datetime.now().isoformat()
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2, ensure_ascii=False)
            print(f"💾 配置已保存到 {config_file}")
            print("⚠️ 注意: 敏感信息(Token、API密钥)未保存到文件中")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def test_github_api(self):
        """测试GitHub API连接"""
        print("\n🔗 测试GitHub API连接...")
        
        try:
            headers = {
                "Authorization": f"token {self.config['github_token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 测试仓库访问
            repo_url = f"https://api.github.com/repos/{self.config['github_username']}/{self.config['github_repo']}"
            response = requests.get(repo_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                repo_info = response.json()
                print(f"✅ 仓库访问成功: {repo_info['full_name']}")
                print(f"   仓库描述: {repo_info.get('description', '无描述')}")
                print(f"   是否私有: {'是' if repo_info['private'] else '否'}")
                return True
            else:
                print(f"❌ 仓库访问失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub API测试异常: {e}")
            return False
    
    def test_youtube_api(self):
        """测试YouTube API"""
        print("\n🎬 测试YouTube API...")
        
        try:
            # 简单的API测试请求
            test_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': 'test',
                'maxResults': 1,
                'key': self.config['youtube_api_key']
            }
            
            response = requests.get(test_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ YouTube API测试成功")
                print(f"   配额消耗: 约100单位")
                print(f"   测试结果数: {len(data.get('items', []))}")
                return True
            else:
                print(f"❌ YouTube API测试失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ YouTube API测试异常: {e}")
            return False
    
    def trigger_test_search(self):
        """触发测试搜索"""
        print("\n🚀 触发测试搜索...")
        
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.config['github_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "event_type": "youtube-search",
                "client_payload": {
                    "search_query": "HONOR 400 test",
                    "max_results": "5",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # 如果有webhook URL，添加到payload中
            if self.config.get('webhook_url'):
                payload["client_payload"]["webhook_url"] = self.config['webhook_url']
            
            dispatch_url = f"https://api.github.com/repos/{self.config['github_username']}/{self.config['github_repo']}/dispatches"
            response = requests.post(dispatch_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 204:
                print("✅ 测试搜索触发成功！")
                actions_url = f"https://github.com/{self.config['github_username']}/{self.config['github_repo']}/actions"
                print(f"🔗 查看执行状态: {actions_url}")
                return True
            else:
                print(f"❌ 测试搜索触发失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试搜索触发异常: {e}")
            return False
    
    def generate_instructions(self):
        """生成部署说明"""
        print("\n📋 生成部署说明...")
        
        instructions = f"""
# GitHub YouTube搜索部署完成

## 🎉 恭喜！部署设置已完成

### 📊 配置摘要
- GitHub仓库: {self.config['github_username']}/{self.config['github_repo']}
- Webhook配置: {'已设置' if self.config.get('webhook_url') else '未设置'}
- 设置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 🔧 GitHub Secrets设置
请在GitHub仓库中设置以下Secret：

1. 进入仓库页面: https://github.com/{self.config['github_username']}/{self.config['github_repo']}
2. 点击 Settings → Secrets and variables → Actions
3. 添加以下Secret:
   - Name: `YOUTUBE_API_KEY`
   - Value: `{self.config['youtube_api_key'][:10]}...` (你的完整API密钥)

### 🚀 使用方法

#### 手动触发搜索:
1. 访问: https://github.com/{self.config['github_username']}/{self.config['github_repo']}/actions
2. 选择 "YouTube Search API" 工作流
3. 点击 "Run workflow"
4. 填写搜索参数并运行

#### API触发搜索:
```bash
curl -X POST \\
  -H "Accept: application/vnd.github.v3+json" \\
  -H "Authorization: token YOUR_GITHUB_TOKEN" \\
  https://api.github.com/repos/{self.config['github_username']}/{self.config['github_repo']}/dispatches \\
  -d '{{
    "event_type": "youtube-search",
    "client_payload": {{
      "search_query": "你的搜索关键词",
      "webhook_url": "{self.config.get('webhook_url', 'YOUR_WEBHOOK_URL')}",
      "max_results": "25"
    }}
  }}'
```

### 📞 技术支持
- 查看执行日志: https://github.com/{self.config['github_username']}/{self.config['github_repo']}/actions
- 问题反馈: 在仓库中创建Issue

---
生成时间: {datetime.now().isoformat()}
"""
        
        try:
            with open('DEPLOYMENT_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
                f.write(instructions)
            print("✅ 部署说明已生成: DEPLOYMENT_INSTRUCTIONS.md")
            return True
        except Exception as e:
            print(f"❌ 生成部署说明失败: {e}")
            return False
    
    def run_setup(self):
        """运行完整设置流程"""
        print("🚀 GitHub YouTube搜索部署设置")
        print("=" * 40)
        
        # 步骤1: 检查文件
        if not self.check_files():
            print("\n❌ 文件检查失败，请确保所有必需文件都存在")
            return False
        
        # 步骤2: 收集配置
        if not self.collect_config():
            print("\n❌ 配置收集失败")
            return False
        
        # 步骤3: 保存配置
        self.save_config()
        
        # 步骤4: 测试GitHub API
        if not self.test_github_api():
            print("\n❌ GitHub API测试失败，请检查Token和仓库信息")
            return False
        
        # 步骤5: 测试YouTube API
        if not self.test_youtube_api():
            print("\n❌ YouTube API测试失败，请检查API密钥")
            return False
        
        # 步骤6: 触发测试搜索
        print("\n🧪 是否要触发一次测试搜索？(y/n): ", end="")
        if input().lower().startswith('y'):
            self.trigger_test_search()
        
        # 步骤7: 生成部署说明
        self.generate_instructions()
        
        print("\n🎉 部署设置完成！")
        print("📋 请查看 DEPLOYMENT_INSTRUCTIONS.md 获取详细使用说明")
        print("🔗 不要忘记在GitHub仓库中设置 YOUTUBE_API_KEY Secret")
        
        return True

def main():
    """主函数"""
    setup = DeploymentSetup()
    
    try:
        setup.run_setup()
    except KeyboardInterrupt:
        print("\n\n⏹️ 设置已取消")
    except Exception as e:
        print(f"\n❌ 设置过程中发生错误: {e}")

if __name__ == "__main__":
    main()