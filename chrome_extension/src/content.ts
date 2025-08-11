// Content script for Chrome extension
// 这个脚本会注入到网页中，可以用于与页面交互

// 监听来自popup或background的消息
chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  // 目前暂时不需要特殊的页面交互功能
  // 可以在这里添加与飞书页面的交互逻辑
  
  if (request.action === 'getPageInfo') {
    // 获取当前页面信息
    const pageInfo = {
      url: window.location.href,
      title: document.title,
      domain: window.location.hostname
    }
    sendResponse({ success: true, data: pageInfo })
  }
  
  return true
})

// 检测是否在飞书页面
if (window.location.hostname.includes('feishu.cn') || window.location.hostname.includes('larksuite.com')) {
  console.log('飞书多维表格助手已加载')
  
  // 可以在这里添加页面增强功能
  // 比如自动提取APP_TOKEN等
}

export {}