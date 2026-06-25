import apiClient from './apiClient';

// 配置相关API
export const getConfig = async (): Promise<any> => {
  return apiClient.get('/v1/config');
};

export const updateConfig = async (config: any): Promise<any> => {
  return apiClient.put('/v1/config', config);
};
