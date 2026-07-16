const { app, BrowserWindow, ipcMain, screen, shell } = require('electron');
const Store = require('electron-store');
const psList = require('ps-list');
const net = require('net');
const { spawn, exec } = require('child_process');
const path = require('path');
const sudo = require('sudo-prompt');
const fs = require('fs');

// Check if current process has admin rights
function isAdmin() {
  try {
    const stats = fs.statSync('C:\\Windows\\System32');
    return true;
  } catch (e) {
    return false;
  }
}

// Request admin rights and restart the application
function restartAsAdmin() {
  return new Promise((resolve, reject) => {
    const options = {
      name: APP_NAME
    };
    const exePath = process.execPath;
    const args = process.argv.slice(1);
    
    sudo.exec(`${exePath} ${args.join(' ')}`, options, (error) => {
      if (error) {
        reject(error);
      } else {
        app.quit();
        resolve();
      }
    });
  });
}

// Initialize store for preferences
const store = new Store();

// Keep track of processes
let frontendProcess = null;
let launchedProcesses = [];

// Create borderless window
function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const windowWidth = 800;
  const windowHeight = 600;
  
  // Determine the appropriate icon to use
  // For development, use __dirname, for production, use process.execPath directory
  let appDirectory;
  if (process.env.NODE_ENV === 'production' || process.execPath.includes('electron-builder')) {
    appDirectory = path.dirname(process.execPath);
  } else {
    appDirectory = __dirname;
  }
  
  // Try multiple possible locations for the icon files
  let iconPath;
  
  // Check .icon-ico directory first (as requested)
  const iconIcoPath = path.join(appDirectory, '.icon-ico', 'icon.ico');
  if (fs.existsSync(iconIcoPath)) {
    console.log('.icon-ico/icon.ico found, using it');
    iconPath = iconIcoPath;
  }
  // Check root directory for PNG icon
  else if (fs.existsSync(path.join(appDirectory, 'icon.png'))) {
    console.log('icon.png found, using it');
    iconPath = path.join(appDirectory, 'icon.png');
  }
  // Check root directory for ICO icon
  else if (fs.existsSync(path.join(appDirectory, 'icon.ico'))) {
    console.log('icon.ico found, using it');
    iconPath = path.join(appDirectory, 'icon.ico');
  }
  // Check for icon in app directory (for production builds)
  else if (fs.existsSync(path.join(appDirectory, 'app', '.icon-ico', 'icon.ico'))) {
    console.log('app/.icon-ico/icon.ico found, using it');
    iconPath = path.join(appDirectory, 'app', '.icon-ico', 'icon.ico');
  }
  // Fallback if no icon found
  else {
    console.error('No icon found in any location!');
    // Use a default icon path, the system will handle the missing icon gracefully
    iconPath = path.join(appDirectory, 'icon.ico');
  }
  
  console.log(`Using icon: ${iconPath}`);

  const mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: Math.round((width - windowWidth) / 2),
    y: Math.round((height - windowHeight) / 2),
    frame: false,
    resizable: false,
    movable: true,
    fullscreenable: false,
    transparent: false,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile(path.join(appDirectory, 'index.html'));
  // mainWindow.webContents.openDevTools();

  return mainWindow;
}

// Check if port is in use
function checkPortInUse(port, host = '127.0.0.1') {
  return new Promise((resolve) => {
    const client = net.createConnection({ port, host }, () => {
      client.end();
      resolve(true);
    });

    client.on('error', () => {
      resolve(false);
    });

    client.setTimeout(1000, () => {
      client.end();
      resolve(false);
    });
  });
}

// Kill process using specific port (Windows only)
function killProcessUsingPort(port) {
  return new Promise((resolve) => {
    spawn('cmd.exe', ['/c', `netstat -ano | findstr :${port}`], {
      windowsHide: true,
      shell: true,
      stdio: 'pipe',
    }).stdout.on('data', (stdout) => {
      const lines = stdout.toString().trim().split('\n');
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid !== '0') {
          spawn('cmd.exe', ['/c', `taskkill /PID ${pid} /F`], {
            windowsHide: true,
            shell: true,
          }).on('error', (killError) => {
            if (killError) {
              console.error(`Failed to kill process ${pid}:`, killError);
            }
          });
        }
      }
      resolve();
    }).on('error', () => {
      resolve();
    });
  });
}

// Check if certificate is already installed
function isCertificateInstalled() {
  return new Promise((resolve) => {
    const timeoutId = setTimeout(() => {
      resolve(false);
    }, 5000); // 5 second timeout

    const command = 'certutil -store "My" | findstr "websiteblocker"';
    
    const process = spawn('cmd.exe', ['/c', command], {
      windowsHide: true,
      shell: true,
      stdio: 'pipe'
    });

    process.stdout.on('data', (stdout) => {
      clearTimeout(timeoutId);
      resolve(stdout.toString().trim().length > 0);
    });

    process.on('error', () => {
      clearTimeout(timeoutId);
      resolve(false);
    });

    process.on('close', () => {
      clearTimeout(timeoutId);
      resolve(false);
    });
  });
}

// Install certificate if not already installed
function installCertificate() {
  return new Promise(async (resolve) => {
    // LICENSE.txt is a license file, not a certificate
    // Skip certificate installation
    console.log('Skipping certificate installation (LICENSE.txt is a license file, not a certificate)');
    store.set('certificateInstalled', true);
    resolve();
  });
}

// Launch executable
function launchExecutable(filePath) {
  return new Promise((resolve) => {
    const process = spawn(filePath, [], {
      detached: true,
      stdio: 'ignore',
      windowsHide: true,
    });
    
    process.unref();
    launchedProcesses.push(process.pid);
    resolve();
  });
}

// Launch backend.exe directly in background without terminal window
function launchBackend() {
  return new Promise((resolve) => {
    // Find backend executable
    let backendPath;

    // For development environment
    const devPath = path.join(__dirname, 'backend', 'WebsiteBlockerBackend.exe');
    if (fs.existsSync(devPath)) {
      backendPath = devPath;
    }
    // For production environment
    else {
      const execPathDir = path.dirname(process.execPath);
      const prodPath1 = path.join(execPathDir, 'backend', 'WebsiteBlockerBackend.exe');

      if (fs.existsSync(prodPath1)) {
        backendPath = prodPath1;
      } else {
        console.error('Could not find WebsiteBlockerBackend.exe in any location');
        isBackendRunning = false;
        resolve();
        return;
      }
    }

    console.log(`Launching backend from: ${backendPath}`);

    frontendProcess = spawn(backendPath, ['-start'], {
      windowsHide: true,  // Ensure no terminal window is shown
      detached: true,     // Run as detached process
      stdio: 'ignore',    // Completely detach from parent process
    });

    frontendProcess.on('error', (error) => {
      console.error('Failed to launch backend:', error);
      isBackendRunning = false;
    });

    frontendProcess.on('close', (code) => {
      console.log(`Backend process exited with code: ${code}`);
      isBackendRunning = false;
    });

    // Detach the process completely from the parent
    frontendProcess.unref();

    isBackendRunning = true;
    resolve();
  });
}

// Send Ctrl+C to process for graceful shutdown
function sendCtrlC(process) {
  if (process && !process.killed) {
    process.kill('SIGINT');
  }
}

// Close all launched processes gracefully
function closeAllProcesses() {
  return new Promise((resolve) => {
    let tasksCompleted = 0;
    const totalTasks = 4; // backend + frontend + browser + node

    // Helper function to check if all tasks are completed
    const checkCompletion = () => {
      tasksCompleted++;
      if (tasksCompleted >= totalTasks) {
        resolve();
      }
    };

    // Gracefully close backend process: send Ctrl+C, wait 1.5 seconds, then close
    if (frontendProcess) {
      sendCtrlC(frontendProcess);

      // Wait 1.5 seconds before checking completion
      setTimeout(() => {
        if (frontendProcess && !frontendProcess.killed) {
          frontendProcess.kill();
        }
        frontendProcess = null;
        isBackendRunning = false;
        checkCompletion();
      }, 1500);
    } else {
      checkCompletion();
    }

    // Terminate all instances of WebsiteBlockerBackend.exe
    spawn('taskkill', ['/F', '/IM', 'WebsiteBlockerBackend.exe', '/T'], {
      windowsHide: true,
    }).on('close', checkCompletion).on('error', checkCompletion);

    // Terminate all instances of WebsiteBlockerFrontend.exe
    spawn('taskkill', ['/F', '/IM', 'WebsiteBlockerFrontend-x86.exe', '/T'], {
      windowsHide: true,
    }).on('close', checkCompletion).on('error', checkCompletion);

    // Terminate all instances of WebsiteBlocker Browser.exe
    spawn('taskkill', ['/F', '/IM', 'WebsiteBlockerBrowser-32bit.exe', '/T'], {
      windowsHide: true,
    }).on('close', checkCompletion).on('error', checkCompletion);
  });
}

// Handle IPC events
function setupIPC(mainWindow) {
  // Check ports and kill processes if needed
  ipcMain.handle('check-ports', async () => {
    const port1 = 16411;
    const port2 = 16410;
    
    const port1InUse = await checkPortInUse(port1);
    const port2InUse = await checkPortInUse(port2);
    
    if (port1InUse) {
      await killProcessUsingPort(port1);
    }
    if (port2InUse) {
      await killProcessUsingPort(port2);
    }
    
    return { port1InUse, port2InUse };
  });

  // Get preferences
  ipcMain.handle('get-preferences', () => {
    return {
      language: store.get('language', 'en'),
      theme: store.get('theme', 'light'),
      isFirstLaunch: !store.has('language'),
    };
  });

  // Save preferences
  ipcMain.handle('save-preferences', (event, preferences) => {
    store.set('language', preferences.language);
    store.set('theme', preferences.theme);
    return true;
  });

  // Start applications
  ipcMain.handle('start-applications', async () => {
    try {
      // Install certificate
      await installCertificate();

      // Helper function to find executable path
      const findExecutablePath = (relativePath) => {
        // Try development path first
        const devPath = path.join(__dirname, relativePath);
        if (fs.existsSync(devPath)) {
          return devPath;
        }

        // Try production paths
        const execPathDir = path.dirname(process.execPath);
        const prodPath1 = path.join(execPathDir, relativePath);
        if (fs.existsSync(prodPath1)) {
          return prodPath1;
        }

        const prodPath2 = path.join(execPathDir, 'resources', 'app', relativePath);
        if (fs.existsSync(prodPath2)) {
          return prodPath2;
        }

        console.error(`Could not find ${relativePath} in any location`);
        return null;
      };

      // Step 1: Launch backend
      const backendPath = findExecutablePath('backend/WebsiteBlockerBackend.exe');
      if (backendPath) {
        await launchBackend();
      }

      // Wait for backend to start
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Step 2: Launch frontend
      const frontendPath = findExecutablePath('frontend/WebsiteBlockerFrontend-x86.exe');
      if (frontendPath) {
        await launchExecutable(frontendPath);
      }

      // Wait for frontend to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 3: Launch browser
      const browserPath = findExecutablePath('browser/WebsiteBlockerBrowser-32bit.exe');
      if (browserPath) {
        await launchExecutable(browserPath);
      }

      return true;
    } catch (error) {
      console.error('Failed to start applications:', error);
      return false;
    }
  });

  // Check if ports are active after startup
  ipcMain.handle('check-ports-active', async () => {
    const port1 = 16411;
    const port2 = 16410;
    
    const port1Active = await checkPortInUse(port1);
    const port2Active = await checkPortInUse(port2);
    
    return { port1Active, port2Active };
  });

  // Close applications
  ipcMain.handle('close-applications', async () => {
    await closeAllProcesses();
    return true;
  });

  // Open email client
  ipcMain.handle('open-email-client', () => {
    const emailUrl = 'mailto:wang.station@hotmail.com';
    spawn('cmd.exe', ['/c', `start "" "${emailUrl}"`], {
      windowsHide: true,
      shell: true,
    }).on('error', (error) => {
      if (error) {
        console.error('Failed to open email client:', error);
      }
    });
    return true;
  });

  // Check if applications are already running
  ipcMain.handle('is-applications-running', () => {
    return isBackendRunning;
  });

  // Quit application
  ipcMain.on('quit-application', () => {
    app.quit();
  });
  
  // Get license file content
  ipcMain.handle('get-license-content', async () => {
    // 定义候选路径列表（按优先级）
    const candidates = [];

    if (app.isPackaged) {
      // 打包后：优先从可执行文件目录找（您说文件在那）
      const exeDir = path.dirname(process.execPath);
      candidates.push(path.join(exeDir, 'LICENSE.txt'));
      // 其次从 resources 目录找（如果使用 extraResources）
      candidates.push(path.join(process.resourcesPath, 'LICENSE.txt'));
      // 再尝试 app.getAppPath() 目录（asar 内部，但可能无意义）
      // candidates.push(path.join(app.getAppPath(), 'LICENSE.txt'));
    } else {
      // 开发环境：项目根目录，根据您的结构调整
      candidates.push(path.join(__dirname, '..', 'LICENSE.txt'));
      candidates.push(path.join(__dirname, 'LICENSE.txt'));
    }

    // 遍历候选路径，读取第一个存在的文件
    for (const licensePath of candidates) {
      try {
        await fs.promises.access(licensePath, fs.constants.R_OK);
        const content = await fs.promises.readFile(licensePath, 'utf8');
        console.log(`License loaded from: ${licensePath}`);
        return content;
      } catch (err) {
        // 忽略错误，继续尝试下一个路径
        console.log(`Cannot read ${licensePath}: ${err.message}`);
      }
    }

    // 所有路径均失败
    console.error('License file not found or unreadable in any candidate location.');
    return null;
  });
}

// Global variables for state management
let mainWindow = null;
let isBackendRunning = false;

// Implement single instance application
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  // Another instance is already running, quit this one
  app.quit();
} else {
  // Handle second instance event
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, focus the existing window
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  // App lifecycle
  app.whenReady().then(async () => {
    // Check if we need admin rights
    if (!isAdmin()) {
      try {
        await restartAsAdmin();
        return;
      } catch (error) {
        console.error('Failed to restart as admin:', error);
        // Continue without admin rights if user declined
      }
    }

    mainWindow = createWindow();
    setupIPC(mainWindow);

    

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        mainWindow = createWindow();
        setupIPC(mainWindow);
      }
    });

    // Ensure all processes are closed when app quits
    app.on('before-quit', async () => {
      await closeAllProcesses();
    });
  });
}



app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
