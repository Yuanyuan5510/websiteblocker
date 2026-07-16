// 渲染进程JavaScript文件
const { ipcRenderer } = require('electron');

// 获取DOM元素
const webview = document.getElementById('webview');
const minimizeBtn = document.getElementById('minimize-btn');
const maximizeBtn = document.getElementById('maximize-btn');
const closeBtn = document.getElementById('close-btn');
const errorOverlay = document.getElementById('error-overlay');
const errorTitle = document.getElementById('error-title');
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');
const loadingOverlay = document.getElementById('loading-overlay');

// 配置
const LOAD_TIMEOUT = 30000; // 30秒超时
const RETRY_DELAY = 2000; // 2秒重试延迟

// 加载超时计时器
let loadTimeout = null;

// 初始化
function init() {
  // 添加事件监听器
  addEventListeners();
  // 显示加载指示器
  showLoading();
}

// 显示加载指示器
function showLoading() {
  loadingOverlay.style.display = 'flex';
  errorOverlay.style.display = 'none';
}

// 隐藏加载指示器
function hideLoading() {
  loadingOverlay.style.display = 'none';
}

// 显示错误提示
function showError(title, message) {
  hideLoading();
  errorTitle.textContent = title;
  errorMessage.textContent = message;
  errorOverlay.style.display = 'flex';
}

// 隐藏错误提示
function hideError() {
  errorOverlay.style.display = 'none';
}

// 设置加载超时
function setLoadTimeout() {
  clearLoadTimeout();
  loadTimeout = setTimeout(() => {
    showError('Connection Timeout', 'The server is not responding. Please check if the server is running and try again.');
  }, LOAD_TIMEOUT);
}

// 清除加载超时
function clearLoadTimeout() {
  if (loadTimeout) {
    clearTimeout(loadTimeout);
    loadTimeout = null;
  }
}

// 重新加载页面
function reloadWebview() {
  hideError();
  showLoading();
  webview.reload();
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
  
  // 重试按钮
  retryBtn.addEventListener('click', () => {
    reloadWebview();
  });
  
  // WebView事件 - 开始加载
  webview.addEventListener('did-start-loading', () => {
    showLoading();
    setLoadTimeout();
  });
  
  // WebView事件 - 加载完成
  webview.addEventListener('did-finish-load', () => {
    hideLoading();
    clearLoadTimeout();
  });
  
  // WebView事件 - 加载失败
  webview.addEventListener('did-fail-load', (e) => {
    clearLoadTimeout();
    hideLoading();
    
    const errorCode = e.errorCode;
    const errorDesc = e.errorDescription || '';
    
    // 根据错误类型显示不同提示
    if (errorCode === -3) {
      // ERR_ABORTED - 通常是用户取消或重定向，不显示错误
      return;
    } else if (errorCode === -21) {
      // ERR_NETWORK_CHANGED
      showError('Network Changed', 'A network change was detected. Please check your network connection and try again.');
    } else if (errorCode === -100) {
      // ERR_CONNECTION_REFUSED
      showError('Connection Refused', 'The server is not running or the port is blocked. Please start the server and try again.');
    } else if (errorCode === -101) {
      // ERR_CONNECTION_RESET
      showError('Connection Reset', 'The connection was reset by the server. Please try again later.');
    } else if (errorCode === -102) {
      // ERR_CONNECTION_REFUSED
      showError('Connection Refused', 'The server refused the connection. Please check if the server is running on port 16410.');
    } else if (errorCode === -105) {
      // ERR_NAME_NOT_RESOLVED
      showError('DNS Error', 'Could not resolve server address. Please check your network connection.');
    } else if (errorCode === -106) {
      // ERR_INTERNET_DISCONNECTED
      showError('No Internet', 'No internet connection detected. Please check your network settings.');
    } else if (errorCode === -118) {
      // ERR_CONNECTION_TIMED_OUT
      showError('Connection Timeout', 'The server is not responding. Please check if the server is running and try again.');
    } else if (errorCode === -21) {
      // ERR_NETWORK_IO_SUSPENDED
      showError('Network Error', 'Network operation was suspended. Please try again.');
    } else if (errorCode === -300) {
      // ERR_INVALID_URL
      showError('Invalid URL', 'The server address is invalid. Please contact support.');
    } else {
      // 其他错误
      showError('Loading Failed', `Failed to load page. Error: ${errorDesc || 'Unknown error'} (Code: ${errorCode}). Please try again.`);
    }
  });
  
  // WebView事件 - 标题更新
  webview.addEventListener('title-updated', (e) => {
    // 更新窗口标题
    document.title = `${e.title} - WebsiteBlocker Browser`;
  });
  
  // WebView事件 - 崩溃
  webview.addEventListener('crashed', () => {
    clearLoadTimeout();
    showError('Application Crashed', 'The application has crashed. Please restart the browser.');
  });
  
  // WebView事件 - 插件崩溃
  webview.addEventListener('plugin-crashed', (e) => {
    console.warn('Plugin crashed:', e.name);
  });
  
  // 处理响应头错误
  webview.addEventListener('did-get-response-details', (e) => {
    if (e.httpResponseCode >= 500) {
      showError('Server Error', `The server returned an error (${e.httpResponseCode}). Please try again later.`);
    }
  });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);