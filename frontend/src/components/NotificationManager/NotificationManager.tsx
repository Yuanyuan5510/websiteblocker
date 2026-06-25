import React, { useState, useEffect } from 'react';
import { getNotificationSettings, updateNotificationSettings, testNotification, isNotificationSupported, requestNotificationPermission } from '../../services/notificationService';
import { t } from '../../i18n/i18n';
import './NotificationManager.css';

interface NotificationSettings {
  enabled: boolean;
  notification_frequency: 'immediate' | 'daily' | 'weekly';
}

const NotificationManager: React.FC = () => {
  // 状态管理
  const [settings, setSettings] = useState<NotificationSettings>({
    enabled: true,
    notification_frequency: 'immediate'
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [notificationSupported, setNotificationSupported] = useState<boolean>(false);
  const [notificationPermission, setNotificationPermission] = useState<boolean>(false);

  // 获取通知设置
  const fetchNotificationSettings = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const notificationSettings = await getNotificationSettings();
      setSettings(notificationSettings);
    } catch (err) {
      setError(t('notification.fetch_error'));
      console.error('Failed to fetch notification settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchNotificationSettings();
    checkNotificationSupport();
  }, []);

  // 检查通知支持情况
  const checkNotificationSupport = async () => {
    const supported = isNotificationSupported();
    setNotificationSupported(supported);
    
    if (supported) {
      const hasPermission = await requestNotificationPermission();
      setNotificationPermission(hasPermission);
    }
  };

  // 请求通知权限
  const handleRequestPermission = async () => {
    const hasPermission = await requestNotificationPermission();
    setNotificationPermission(hasPermission);
  };

  // 更新通知设置
  const handleUpdateSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await updateNotificationSettings(settings);
      setSuccess(t('notification.save_success'));
    } catch (err) {
      setError(t('notification.save_error'));
      console.error('Failed to update notification settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 测试通知
  const handleTestNotification = async () => {
    setIsTesting(true);
    setError(null);
    setSuccess(null);
    
    try {
      await testNotification();
      setSuccess(t('notification.test_success'));
    } catch (err) {
      setError(t('notification.test_error'));
      console.error('Failed to test notification:', err);
    } finally {
      setIsTesting(false);
    }
  };

  // 处理设置变化
  const handleSettingChange = (field: keyof NotificationSettings, value: any) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="notification-manager">
      <div className="notification-manager-header">
        <h2>{t('notification.title')}</h2>
      </div>

      {/* 消息提示 */}
      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      {/* 通知设置表单 */}
      <div className="notification-settings-form">
        <h3>{t('notification.subtitle')}</h3>
        
        {isLoading && !isTesting ? (
          <div className="loading">{t('notification.loading')}</div>
        ) : (
          <form onSubmit={handleUpdateSettings}>
            {/* 系统通知支持检查 */}
            <div className="form-section">
              <h4>{t('notification.system_support')}</h4>
              {!notificationSupported ? (
                <div className="system-notification-status error">
                  {t('notification.browser_not_supported')}
                </div>
              ) : (
                <div className="system-notification-status">
                  <div className="notification-status-item">
                    <strong>{t('notification.browser_support')}：</strong> 支持
                  </div>
                  <div className="notification-status-item">
                    <strong>{t('notification.permission')}：</strong> 
                    {notificationPermission ? (
                      <span className="status-success">{t('notification.permission_granted')}</span>
                    ) : (
                      <span className="status-error">{t('notification.permission_denied')}</span>
                    )}
                  </div>
                  {!notificationPermission && (
                    <div className="permission-action">
                      <button 
                        type="button" 
                        className="btn btn-sm btn-primary"
                        onClick={handleRequestPermission}
                      >
                        {t('notification.request_permission')}
                      </button>
                      <p className="permission-hint">
                        {t('notification.permission_hint')}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="form-section">
              <h4>{t('notification.basic_settings')}</h4>
              <div className="form-row">
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={settings.enabled}
                      onChange={(e) => handleSettingChange('enabled', e.target.checked)}
                    />
                    <span className="checkbox-text">{t('notification.enable_notifications')}</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div className="form-section">
              <h4>{t('notification.notification_preferences')}</h4>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="notification_frequency">{t('notification.notification_frequency')}</label>
                  <select
                    id="notification_frequency"
                    value={settings.notification_frequency}
                    onChange={(e) => handleSettingChange('notification_frequency', e.target.value as any)}
                    disabled={!settings.enabled}
                  >
                    <option value="immediate">{t('notification.frequency_immediate')}</option>
                    <option value="daily">{t('notification.frequency_daily')}</option>
                    <option value="weekly">{t('notification.frequency_weekly')}</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="form-actions">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? t('notification.save_loading') : t('notification.save')}
              </button>
              
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleTestNotification}
                disabled={isTesting || !settings.enabled || !notificationPermission}
              >
                {isTesting ? t('notification.test_loading') : t('notification.test')}
              </button>
            </div>
          </form>
        )}
      </div>

      {/* 通知说明 */}
      <div className="notification-info">
        <h3>{t('notification.info_title')}</h3>
        <div className="info-content">
          <p>{t('notification.info_description')}</p>
          <h4>{t('notification.notification_types')}</h4>
          <ul>
            <li>{t('notification.notification_type_1')}</li>
            <li>{t('notification.notification_type_2')}</li>
            <li>{t('notification.notification_type_3')}</li>
            <li>{t('notification.notification_type_4')}</li>
            <li>{t('notification.notification_type_5')}</li>
          </ul>
          <h4>{t('notification.frequency_explanation')}</h4>
          <ul>
            <li>{t('notification.frequency_explanation_immediate')}</li>
            <li>{t('notification.frequency_explanation_daily')}</li>
            <li>{t('notification.frequency_explanation_weekly')}</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default NotificationManager;
