import apiClient from './apiClient';

// 检查浏览器是否支持通知
export const isNotificationSupported = (): boolean => {
  return 'Notification' in window;
};

// 请求通知权限
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!isNotificationSupported()) {
    return false;
  }
  
  if (Notification.permission === 'granted') {
    return true;
  }
  
  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  
  return false;
};

// 发送系统通知
export const sendSystemNotification = (title: string, options: NotificationOptions = {}): void => {
  if (!isNotificationSupported() || Notification.permission !== 'granted') {
    console.warn('系统通知不支持或未获得授权');
    return;
  }
  
  try {
    new Notification(title, options);
  } catch (error) {
    console.error('发送系统通知失败:', error);
  }
};

// 通知相关API
export const getNotificationSettings = async (): Promise<any> => {
  return apiClient.get('/v1/notifications/config');
};

export const updateNotificationSettings = async (settings: any): Promise<any> => {
  return apiClient.put('/v1/notifications/config', settings);
};

export const testNotification = async (): Promise<{ success: boolean; message: string }> => {
  // 先请求通知权限
  const hasPermission = await requestNotificationPermission();
  if (hasPermission) {
    // 发送测试通知
    sendSystemNotification('测试通知', {
      body: '这是一条测试通知，用于验证通知功能是否正常工作。',
      icon: '/favicon.ico',
      tag: 'test-notification'
    });
  }
  return apiClient.post('/v1/notifications/toggle');
};
