// 渲染进程JavaScript文件
const { ipcRenderer } = require('electron');

// 获取DOM元素
const webview = document.getElementById('webview');
const minimizeBtn = document.getElementById('minimize-btn');
const maximizeBtn = document.getElementById('maximize-btn');
const closeBtn = document.getElementById('close-btn');

// 初始化
function init() {
  // 添加事件监听器
  addEventListeners();
}

// 添加事件监听器
function addEventListeners() {
  // 窗口控制按钮事件
  minimizeBtn.addEventListener('click', () => {
    ipcRenderer.send('minimize-window');
  });
  
  maximizeBtn.addEventListener('click', () => {
    ipcRenderer.send('maximize-window');
  });
  
  closeBtn.addEventListener('click', () => {
    ipcRenderer.send('close-window');
  });
  
  // WebView事件
  webview.addEventListener('title-updated', (e) => {
    // 更新窗口标题
    document.title = `${e.title} - 网站访问限制浏览器`;
  });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
