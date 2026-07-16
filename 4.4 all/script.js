const { ipcRenderer } = require('electron');

// Internationalization strings
const i18n = {
    en: {
        admin_program: 'Admin Program',
        select_language: 'Select Language',
        select_theme: 'Select Theme',
        light: 'Light',
        dark: 'Dark',
        welcome: 'Welcome',
        start: 'Start',
        close: 'Close',
        applications_running: 'Applications Running',
        applications_running_desc: 'The website blocker applications are now running.',
        tray_notice: 'If you don\'t see other GUI windows, please check the system tray.',
        feedback: 'Feedback',
        initializing: 'Initializing...',
        checking_ports: 'Checking ports...',
        installing_certificate: 'Installing certificate...',
        starting_applications: 'Starting Applications...',
        please_wait: 'Please wait...',
        closing: 'Closing...',
        startup_complete: 'Startup Complete',
        closing_applications: 'Closing applications...',
        shutting_down: 'Shutting down...',
        email_feedback: 'Send Feedback',
        port_error: 'Port error detected',
        permission_error: 'Permission error',
        certificate_installed: 'Certificate installed successfully',
        certificate_error: 'Certificate installation failed',
        process_error: 'Process error',
        admin_required: 'Admin rights required',
        restarting_as_admin: 'Restarting with admin rights...',
        development_mode: 'Development Mode',
        highest_priority: 'Highest Priority',
        english: 'English',
        chinese: '中文',
        license_agreement: 'License Agreement',
        back: 'Back',
        view_license: 'View License'
    },
    zh: {
        admin_program: '管理员程序',
        select_language: '选择语言',
        select_theme: '选择主题',
        light: '浅色',
        dark: '深色',
        welcome: '欢迎',
        start: '启动',
        close: '关闭',
        applications_running: '应用程序正在运行',
        applications_running_desc: '网站拦截器应用程序现已运行。',
        tray_notice: '如果没有看到其他界面，请查看系统托盘。',
        feedback: '反馈',
        initializing: '初始化中...',
        checking_ports: '检查端口...',
        installing_certificate: '安装证书...',
        starting_applications: '启动应用程序...',
        please_wait: '请稍候...',
        closing: '关闭中...',
        startup_complete: '启动完成',
        closing_applications: '关闭应用程序...',
        shutting_down: '正在关闭...',
        email_feedback: '发送反馈',
        port_error: '检测到端口错误',
        permission_error: '权限错误',
        certificate_installed: '证书安装成功',
        certificate_error: '证书安装失败',
        process_error: '进程错误',
        admin_required: '需要管理员权限',
        restarting_as_admin: '以管理员权限重启...',
        development_mode: '开发模式',
        highest_priority: '最高优先级',
        english: '英语',
        chinese: '中文',
        license_agreement: '许可证协议',
        back: '返回',
        view_license: '查看许可证'
    }
};

// Global variables
let currentLanguage = 'en';
let currentTheme = 'light';

// Initialize the application
async function init() {
    // Get preferences from main process
    const preferences = await ipcRenderer.invoke('get-preferences');
    currentLanguage = preferences.language;
    currentTheme = preferences.theme;
    
    // Set initial theme
    document.body.className = `${currentTheme}-theme`;
    
    // Start startup animation and port checking
    await startStartupFlow();
}

// Switch screen
function switchScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
    }
}

// Set language
function setLanguage(lang) {
    currentLanguage = lang;
    translatePage();
}

// Translate page elements
function translatePage() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (i18n[currentLanguage][key]) {
            element.textContent = i18n[currentLanguage][key];
        }
    });
}

// Set theme
function setTheme(theme) {
    currentTheme = theme;
    document.body.className = `${theme}-theme`;
}

// Start startup flow
async function startStartupFlow() {
    // Show startup screen
    switchScreen('startup-screen');
    
    try {
        // Update status text
        updateStatusText('initializing');
        
        // Check ports and kill processes if needed with timeout
        updateStatusText('checking_ports');
        await withTimeout(ipcRenderer.invoke('check-ports'), 10000);
        
        // Wait for startup animation to complete (2.5 seconds - reduced from 3)
        updateStatusText('please_wait');
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        // Check if it's first launch with timeout
        const preferences = await withTimeout(ipcRenderer.invoke('get-preferences'), 5000);
        
        if (preferences.isFirstLaunch) {
            // Show language selection
            switchScreen('language-screen');
        } else {
            // Load preferences and go to start/close screen
            setLanguage(preferences.language);
            setTheme(preferences.theme);
            switchScreen('start-close-screen');
        }
    } catch (error) {
        console.error('Startup flow error:', error);
        // If any step fails, show error and go to start/close screen
        const statusText = document.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = i18n[currentLanguage]['process_error'] || 'Process error';
        }
        
        // Wait briefly to show error, then go to start/close screen
        await new Promise(resolve => setTimeout(resolve, 2000));
        switchScreen('start-close-screen');
    }
}

// Save preferences
async function savePreferences() {
    await ipcRenderer.invoke('save-preferences', {
        language: currentLanguage,
        theme: currentTheme
    });
}

// Helper function with timeout
function withTimeout(promise, timeout = 10000) {
    return Promise.race([
        promise,
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Operation timed out')), timeout)
        )
    ]);
}

// Update status text on startup screen
function updateStatusText(textKey) {
    const statusText = document.querySelector('.status-text');
    if (statusText) {
        statusText.textContent = i18n[currentLanguage][textKey] || textKey;
    }
}

// Handle start button click
async function handleStartClick() {
    // Check if applications are already running
    const isRunning = await ipcRenderer.invoke('is-applications-running');
    
    if (isRunning) {
        // If already running, directly switch to feedback/close page
        switchScreen('post-startup-screen');
        return;
    }
    
    // Show starting screen
    switchScreen('app-starting-screen');
    
    try {
        // Start applications in parallel with showing startup page
        const startupPromise = withTimeout(ipcRenderer.invoke('start-applications'), 20000);
        
        // Show startup page for full 25 seconds with proper status updates
        const totalStartupTime = 25000;
        const startTime = Date.now();
        
        // Update status text at different stages
        updateStatusText('starting_applications');
        
        // First stage: 8 seconds
        await new Promise(resolve => setTimeout(resolve, 8000));
        updateStatusText('installing_certificate');
        
        // Second stage: 7 seconds  
        await new Promise(resolve => setTimeout(resolve, 7000));
        updateStatusText('checking_ports');
        
        // Wait for startup to complete if it hasn't already
        await startupPromise;
        
        // Calculate remaining time to reach full 25 seconds
        const elapsedTime = Date.now() - startTime;
        const remainingTime = Math.max(0, totalStartupTime - elapsedTime);
        
        if (remainingTime > 0) {
            await new Promise(resolve => setTimeout(resolve, remainingTime));
        }
        
        // Always switch to post startup screen after successful launch
        switchScreen('post-startup-screen');
        
        // Add a safety check to ensure we stay on the correct page
        setTimeout(() => {
            // Verify we're still on the correct page
            const activeScreen = document.querySelector('.screen.active');
            if (activeScreen && activeScreen.id !== 'post-startup-screen') {
                switchScreen('post-startup-screen');
            }
        }, 1000);
    } catch (error) {
        console.error('Startup error:', error);
        // If any step fails, return to start/close screen
        switchScreen('start-close-screen');
    }
}

// Handle close button click
async function handleCloseClick() {
    // Show closing screen
    switchScreen('closing-screen');
    
    // Wait for closing animation (5 seconds)
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Quit application
    ipcRenderer.send('quit-application');
}

// Handle post startup close click
async function handlePostStartupCloseClick() {
    // Show closing screen
    switchScreen('closing-screen');
    
    // Close applications
    await ipcRenderer.invoke('close-applications');
    
    // Wait for closing animation (5 seconds)
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Quit application
    ipcRenderer.send('quit-application');
}

// Handle feedback button click
async function handleFeedbackClick() {
    await ipcRenderer.invoke('open-email-client');
}

// Load and display license content
async function loadAndDisplayLicense() {
    try {
        const licenseContent = await ipcRenderer.invoke('get-license-content');
        const certificateTextElement = document.getElementById('certificate-text');
        
        if (licenseContent) {
            certificateTextElement.textContent = licenseContent;
        } else {
            certificateTextElement.textContent = 'Failed to load license file. Please check if the file exists and has the correct permissions.';
        }
    } catch (error) {
        console.error('Error loading license content:', error);
        const certificateTextElement = document.getElementById('certificate-text');
        certificateTextElement.textContent = 'Error loading license file: ' + error.message;
    }
}

// Handle view license button click
async function handleViewLicenseClick() {
    await loadAndDisplayLicense();
    switchScreen('certificate-screen');
}

// Handle back to main button click
function handleBackToMainClick() {
    switchScreen('post-startup-screen');
}

// Event listeners
function setupEventListeners() {
    // Language selection buttons
    document.querySelectorAll('.language-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            setLanguage(lang);
            switchScreen('theme-screen');
        });
    });
    
    // Theme selection buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const theme = btn.getAttribute('data-theme');
            setTheme(theme);
            await savePreferences();
            switchScreen('start-close-screen');
        });
    });
    
    // Start button
    document.getElementById('start-btn').addEventListener('click', handleStartClick);
    
    // Close button
    document.getElementById('close-btn').addEventListener('click', handleCloseClick);
    
    // Post startup close button
    document.getElementById('post-close-btn').addEventListener('click', handlePostStartupCloseClick);
    
    // Feedback button
    document.getElementById('feedback-btn').addEventListener('click', handleFeedbackClick);
    
    // View license button
    document.getElementById('view-license-btn').addEventListener('click', handleViewLicenseClick);
    
    // Back to main button
    document.getElementById('back-to-main').addEventListener('click', handleBackToMainClick);
}

// Global terminal variables
let terminal = null;
let fitAddon = null;
let terminalContainer = null;

// Initialize terminal
function initTerminal() {
    // Create terminal instance
    terminal = new Terminal({
        cursorBlink: true,
        theme: {
            background: currentTheme === 'dark' ? '#1e1e1e' : '#ffffff',
            foreground: currentTheme === 'dark' ? '#cccccc' : '#333333'
        }
    });
    
    // Create fit addon
    fitAddon = new FitAddon.FitAddon();
    
    // Load fit addon
    terminal.loadAddon(fitAddon);
    
    // Get terminal container
    terminalContainer = document.getElementById('terminal-container');
    const terminalElement = document.getElementById('terminal');
    
    // Attach terminal to DOM
    terminal.open(terminalElement);
    
    // Fit terminal to container
    fitAddon.fit();
    
    // Handle terminal resize
    window.addEventListener('resize', () => {
        if (terminal && fitAddon && terminalContainer.style.display !== 'none') {
            fitAddon.fit();
        }
    });
    
    // Add terminal event listeners
    setupTerminalEventListeners();
    
    // Write welcome message
    terminal.write(`Website Blocker Terminal\n`);
    terminal.write(`Type 'help' for available commands\n\n`);
}

// Setup terminal event listeners
function setupTerminalEventListeners() {
    // Terminal close button
    document.getElementById('close-terminal').addEventListener('click', () => {
        hideTerminal();
    });
    
    // Terminal minimize button
    document.getElementById('minimize-terminal').addEventListener('click', () => {
        hideTerminal();
    });
    
    // Terminal maximize button
    document.getElementById('maximize-terminal').addEventListener('click', () => {
        toggleTerminalMaximize();
    });
    
    // Handle terminal input
    terminal.onData((data) => {
        handleTerminalInput(data);
    });
}

// Show terminal
function showTerminal() {
    if (!terminal) {
        initTerminal();
    }
    terminalContainer.style.display = 'flex';
    fitAddon.fit();
    terminal.focus();
}

// Hide terminal
function hideTerminal() {
    terminalContainer.style.display = 'none';
}

// Toggle terminal maximize
function toggleTerminalMaximize() {
    const currentHeight = terminalContainer.style.height;
    if (currentHeight === '100%') {
        terminalContainer.style.height = '300px';
    } else {
        terminalContainer.style.height = '100%';
    }
    fitAddon.fit();
}

// Handle terminal input
function handleTerminalInput(data) {
    // Echo input to terminal
    terminal.write(data);
    
    // Handle special keys
    if (data === '\r') { // Enter key
        terminal.write('\n');
        // Process command here (placeholder)
        terminal.write('> ');
    } else if (data === '\x7f') { // Backspace key
        // Handle backspace
        terminal.write('\b \b');
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    init();
    // Initialize terminal after a short delay
    setTimeout(initTerminal, 1000);
});
