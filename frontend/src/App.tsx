import React, { useState, useEffect } from 'react';
import './style.css';
import DomainManager from './components/DomainManager/DomainManager';
import HostsManager from './components/HostsManager/HostsManager';
import ScheduleManager from './components/ScheduleManager/ScheduleManager';
import NotificationManager from './components/NotificationManager/NotificationManager';
import TemplateManager from './components/TemplateManager/TemplateManager';
import UpdateNotification from './components/UpdateNotification/UpdateNotification';
import { t, setLanguage, getLanguage } from './i18n/i18n';
import type { Language, TranslationKeyPaths } from './i18n/i18n';
import websocketService from './services/websocketService';
import updateChecker from './services/UpdateChecker';


// 定义导航项类型
interface NavItem {
  id: string;
  nameKey: TranslationKeyPaths;
  component: React.ReactNode;
  icon: string;
}

// 定义主题类型
type Theme = 'light' | 'dark';

const App: React.FC = () => {
  // 状态管理
  const [activeNav, setActiveNav] = useState<string>('domains');
  const [language, setLanguageState] = useState<Language>(getLanguage());
  const [theme, setThemeState] = useState<Theme>('light');
  const [showSettings, setShowSettings] = useState<boolean>(false);
  
  // 更新检查状态
  const [showUpdateNotification, setShowUpdateNotification] = useState<boolean>(false);
  const [latestVersion, setLatestVersion] = useState<string>('4.4');
  const [isCheckingUpdate, setIsCheckingUpdate] = useState<boolean>(false);

  // 初始化主题设置
  useEffect(() => {
    // 从localStorage获取保存的主题设置，默认使用浅色主题
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const currentTheme = savedTheme || 'light';
    setThemeState(currentTheme);
    document.documentElement.setAttribute('data-theme', currentTheme);
  }, []);

  // 初始化WebSocket连接
  useEffect(() => {
    // 连接WebSocket服务器
    websocketService.connect();

    // 添加全局消息监听器
    const handleWebSocketMessage = (message: any) => {
      console.log('处理WebSocket消息:', message);
      // 可以在这里添加全局消息处理逻辑
    };

    websocketService.on('*', handleWebSocketMessage);

    // 组件卸载时关闭WebSocket连接
    return () => {
      websocketService.off('*', handleWebSocketMessage);
      websocketService.close();
    };
  }, []);
  
  // 检查更新的函数
  const checkForUpdates = async () => {
    if (isCheckingUpdate) return;
    
    setIsCheckingUpdate(true);
    
    try {
      const result = await updateChecker.manualCheck();
      if (result.hasUpdate) {
        setLatestVersion(result.latestVersion);
        setShowUpdateNotification(true);
      }
    } catch (error) {
      console.error('Failed to check for updates:', error);
    } finally {
      setIsCheckingUpdate(false);
    }
  };
  
  // 初始化更新检查
  useEffect(() => {
    // 检查是否需要进行更新检查
    if (updateChecker.shouldCheckForUpdates()) {
      checkForUpdates();
    }
    
    // 设置定期检查，每天检查一次
    const interval = setInterval(() => {
      if (updateChecker.shouldCheckForUpdates()) {
        checkForUpdates();
      }
    }, 24 * 60 * 60 * 1000); // 24小时
    
    // 组件卸载时清除定时器
    return () => clearInterval(interval);
  }, [isCheckingUpdate]);
  
  // 处理更新操作
  const handleUpdate = () => {
    // 这里可以添加实际的更新逻辑
    console.log('Updating to version:', latestVersion);
    // 例如：window.open('https://example.com/download', '_blank');
  };
  
  // 处理关闭更新通知
  const handleCloseUpdateNotification = () => {
    setShowUpdateNotification(false);
  };

  // 导航配置
  const navItems: NavItem[] = [
    {
      id: 'domains',
      nameKey: 'nav.domains',
      component: <DomainManager />,
      icon: '🌐'
    },
    {
      id: 'hosts',
      nameKey: 'nav.hosts',
      component: <HostsManager />,
      icon: '📋'
    },
    {
      id: 'schedules',
      nameKey: 'nav.schedules',
      component: <ScheduleManager />,
      icon: '⏰'
    },
    {
      id: 'notifications',
      nameKey: 'nav.notifications',
      component: <NotificationManager />,
      icon: '🔔'
    },
    {
      id: 'templates',
      nameKey: 'nav.templates',
      component: <TemplateManager />,
      icon: '📁'
    }
  ];

  // 处理语言切换
  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    setLanguageState(newLanguage);
  };

  // 处理主题切换
  const handleThemeChange = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  return (
    <div className="app">
      {/* 头部 */}
      <header className="app-header">
        <h1>{t('app.title')}</h1>
        
        {/* 设置按钮 */}
        <button 
          className="settings-btn" 
          onClick={() => setShowSettings(!showSettings)}
          aria-label="设置"
        >
          ⚙️
        </button>
        
        {/* 设置菜单 */}
        {showSettings && (
          <div className="settings-menu">
            <h3>{t('app.title')} - {t('settings.language')}</h3>
            
            <div className="setting-item">
              <label>{t('settings.language')}:</label>
              <select 
                className="select"
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value as Language)}
              >
                <option value="zh">{t('settings.chinese')}</option>
                <option value="en">{t('settings.english')}</option>
              </select>
            </div>
            
            <div className="setting-item">
              <label>{t('settings.theme')}:</label>
              <select 
                className="select"
                value={theme}
                onChange={(e) => handleThemeChange(e.target.value as Theme)}
              >
                <option value="light">{t('settings.light')}</option>
                <option value="dark">{t('settings.dark')}</option>
              </select>
            </div>
          </div>
        )}
      </header>

      {/* 主体内容 */}
      <div className="app-container">
        {/* 侧边导航 */}
        <aside className="app-sidebar">
          <nav className="app-nav">
            {navItems.map(item => (
              <button
                key={item.id}
                className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
                onClick={() => setActiveNav(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-name">{t(item.nameKey)}</span>
              </button>
            ))}
          </nav>
        </aside>

        {/* 主内容区域 */}
        <main className="app-content">
          {navItems.find(item => item.id === activeNav)?.component}
        </main>
      </div>

      {/* 页脚 */}
      <footer className="app-footer">
        <p>{t('app.copyright')}</p>
      </footer>

      {/* 更新通知 */}
      {showUpdateNotification && (
        <UpdateNotification
          latestVersion={latestVersion}
          currentVersion="4.4"
          onClose={handleCloseUpdateNotification}
          onUpdate={handleUpdate}
        />
      )}
    </div>
  );
};

export default App;
