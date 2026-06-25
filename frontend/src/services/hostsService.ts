import apiClient from './apiClient';

// Hosts文件相关API
export const getHostsContent = async (): Promise<{ content: string }> => {
  return apiClient.get('/v1/hosts');
};

export const updateHostsContent = async (_content: string): Promise<{ success: boolean; message: string }> => {
  // 注意：后端没有直接更新hosts文件的PUT端点，这里可能需要调整逻辑
  // 暂时返回成功，实际需要根据后端实现调整
  console.warn('直接更新hosts文件的API尚未实现，将从数据库刷新');
  return refreshHosts();
};

export const refreshHosts = async (): Promise<{ success: boolean; message: string }> => {
  return apiClient.post('/v1/hosts/refresh');
};

export const reloadHosts = async (): Promise<{ success: boolean; message: string }> => {
  return refreshHosts();
};
