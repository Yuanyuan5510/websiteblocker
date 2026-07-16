const { app, BrowserWindow, Tray, Menu, ipcMain, nativeImage } = require('electron');
const path = require('path');
const fs = require('fs');

// 保持对窗口对象的全局引用
let mainWindow;
let tray;
let splashWindow;
let loadingProgress = 0;

// 创建系统托盘
function createTray() {
  const iconPath = path.join(__dirname, 'app_icon.png');
  const icon = nativeImage.createFromPath(iconPath);
  
  tray = new Tray(icon);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
        }
      }
    },
    {
      label: '退出应用',
      click: () => {
        app.quit();
      }
    }
  ]);
  
  tray.setToolTip('Website Blocker Browser');
  tray.setContextMenu(contextMenu);
  
  // 点击托盘图标切换窗口显示/隐藏
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
      }
    }
  });
}

// 创建启动动画窗口
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 300,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  
  splashWindow.loadFile('splash.html');
  
  // 记录启动开始时间
  const startTime = Date.now();
  const minDuration = 2000; // 最小动画持续时间（毫秒）
  
  // 启动进度模拟
  const progressInterval = setInterval(() => {
    // 计算已过时间
    const elapsedTime = Date.now() - startTime;
    
    // 根据已过时间和最小持续时间计算进度
    // 确保进度在动画持续期间平滑增长
    loadingProgress = Math.min(elapsedTime / minDuration, 1);
    
    if (loadingProgress >= 1) {
      clearInterval(progressInterval);
      // 关闭启动窗口并创建主窗口
      if (splashWindow) {
        splashWindow.close();
        splashWindow = null;
      }
      createMainWindow();
    } else {
      // 向渲染进程发送进度更新
      if (splashWindow && splashWindow.webContents) {
        splashWindow.webContents.send('loading-progress', loadingProgress);
      }
    }
  }, 100); // 更频繁的进度更新，使动画更流畅
}

// 创建主窗口
function createMainWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    frame: false, // 无边框窗口
    titleBarStyle: 'hidden',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true
    },
    title: '网站访问限制浏览器',
    icon: path.join(__dirname, 'app_icon.png')
  });

  // 加载应用的index.html
  mainWindow.loadFile('index.html');

  // 打开开发者工具（生产环境中应该关闭）
  // mainWindow.webContents.openDevTools();

  // 当窗口关闭时触发此事件
  mainWindow.on('closed', function () {
    // 取消引用窗口对象
    mainWindow = null;
  });
}

// 应用就绪事件
app.on('ready', () => {
  createTray();
  createSplashWindow();
});

// 当所有窗口都关闭时，保持应用运行（仅在Windows上）
app.on('window-all-closed', function () {
  // 在Windows和Linux上，当所有窗口关闭时退出应用
  // 但我们希望应用继续在系统托盘中运行
  // 所以注释掉默认的退出逻辑
  // if (process.platform !== 'darwin') app.quit();
});

// 激活事件（点击dock图标或任务栏图标）
app.on('activate', function () {
  // 在macOS上，当点击dock图标并且没有其他窗口打开时，创建一个新窗口
  if (mainWindow === null) {
    createMainWindow();
  }
});

// IPC事件处理
ipcMain.on('close-window', () => {
  if (mainWindow) {
    mainWindow.hide();
  }
});

ipcMain.on('minimize-window', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

// 在这个文件中，你可以续写应用剩下主进程代码，也可以拆分成几个文件，然后用require导入
