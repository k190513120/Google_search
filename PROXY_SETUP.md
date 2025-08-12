# 代理设置说明

由于在中国大陆访问YouTube API需要代理，本项目支持多种代理配置方式。

## 支持的代理类型

### 1. SOCKS代理（推荐）
```bash
export SOCKS_PROXY="socks5://127.0.0.1:1080"
# 或者
export SOCKS_PROXY="socks4://127.0.0.1:1080"
```

### 2. HTTP代理
```bash
export HTTP_PROXY="http://127.0.0.1:8080"
```

### 3. HTTPS代理
```bash
export HTTPS_PROXY="https://127.0.0.1:8080"
```

## 使用方法

### 方法1：设置环境变量后运行
```bash
# 设置代理
export SOCKS_PROXY="socks5://127.0.0.1:1080"

# 运行评论获取
python3 youtube_search_webhook.py comments VIDEO_ID 10 YOUR_API_KEY

# 运行视频搜索
python3 youtube_search_webhook.py search "搜索关键词" 10 YOUR_API_KEY
```

### 方法2：一行命令设置代理并运行
```bash
# 评论获取
SOCKS_PROXY="socks5://127.0.0.1:1080" python3 youtube_search_webhook.py comments VIDEO_ID 10 YOUR_API_KEY

# 视频搜索
SOCKS_PROXY="socks5://127.0.0.1:1080" python3 youtube_search_webhook.py search "搜索关键词" 10 YOUR_API_KEY
```

## 代理优先级

程序会按以下优先级检查代理设置：
1. `SOCKS_PROXY`（最高优先级）
2. `HTTPS_PROXY`
3. `HTTP_PROXY`（最低优先级）

## 常见代理软件端口

- **Clash**: 通常使用 `socks5://127.0.0.1:7890` 或 `http://127.0.0.1:7890`
- **V2Ray**: 通常使用 `socks5://127.0.0.1:1080`
- **Shadowsocks**: 通常使用 `socks5://127.0.0.1:1080`

## 测试代理是否工作

运行程序时，如果使用了代理，会显示：
```
🌐 使用代理: socks5://127.0.0.1:1080
```

如果没有显示此信息，说明没有检测到代理配置。

## 注意事项

1. 确保代理软件正在运行
2. 确保代理端口号正确
3. 如果使用SOCKS代理，确保已安装 `PySocks` 依赖包
4. 代理地址格式要正确，包含协议前缀（如 `socks5://` 或 `http://`）