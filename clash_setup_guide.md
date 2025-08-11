# Clash代理设置指南

## 问题说明
当前YouTube API请求直连超时，需要使用代理访问。您已提供了Clash配置文件，现在需要启动Clash代理服务。

## 解决方案

### 方法1：使用ClashX（推荐，适用于macOS）

1. **下载并安装ClashX**
   - 访问：https://github.com/yichengchen/clashX/releases
   - 下载最新版本的ClashX.dmg
   - 安装到应用程序文件夹

2. **导入配置文件**
   - 启动ClashX
   - 点击菜单栏的ClashX图标
   - 选择「配置」→「托管配置」→「管理」
   - 点击「添加」，输入您的配置URL：
     ```
     https://s1.trojanflare.one/clashx/01791913-ef81-4881-99e2-965fd6fef80a
     ```
   - 点击「确定」下载配置

3. **启用代理**
   - 在ClashX菜单中选择刚下载的配置
   - 点击「设为系统代理」
   - 确保「出站模式」设置为「规则判断」

4. **验证代理状态**
   - ClashX会在端口7890提供HTTP代理
   - 端口7891提供SOCKS代理

### 方法2：使用命令行Clash

1. **安装Clash**
   ```bash
   # 使用Homebrew安装
   brew install clash
   ```

2. **下载配置文件**
   ```bash
   # 创建配置目录
   mkdir -p ~/.config/clash
   
   # 下载配置文件
   curl -o ~/.config/clash/config.yaml "https://s1.trojanflare.one/clashx/01791913-ef81-4881-99e2-965fd6fef80a"
   ```

3. **启动Clash**
   ```bash
   # 启动Clash（会占用终端）
   clash -d ~/.config/clash
   
   # 或者后台运行
   nohup clash -d ~/.config/clash > /dev/null 2>&1 &
   ```

## 使用代理运行Python脚本

启动Clash后，修改`youtube_search.py`中的代理设置：

```python
USE_PROXY = True  # 启用代理
PROXY_HOST = "127.0.0.1"  # 本地地址
PROXY_PORT = 7890  # HTTP代理端口
PROXY_TYPE = "HTTP"  # 代理类型
```

然后运行脚本：
```bash
python3 youtube_search.py
```

## 验证代理是否工作

可以使用以下命令测试代理：
```bash
# 测试HTTP代理
curl --proxy http://127.0.0.1:7890 https://www.google.com

# 测试SOCKS代理
curl --socks5 127.0.0.1:7891 https://www.google.com
```

## 常见问题

1. **端口被占用**：检查是否有其他程序使用了7890端口
2. **配置文件无效**：确保URL可以正常访问
3. **网络连接问题**：确保本地网络可以访问配置文件URL

## 注意事项

- 配置文件显示有效期至2026-03-31
- 剩余流量62.16 GB
- 包含多个香港、日本、美国、澳洲节点
- 建议选择延迟较低的香港节点