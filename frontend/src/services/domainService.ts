import apiClient from './apiClient';

// 类型定义
export interface Domain {
  id: number;
  domain: string;
  reason: string;
  category?: string;
  active?: boolean;
  created_at: string;
}

export interface CreateDomainData {
  domain: string;
  reason: string;
  category?: string;
}

export interface UpdateDomainData {
  reason?: string;
  category?: string;
  active?: boolean;
}

// 批量添加域名类型定义
export interface BatchDomainData {
  domains: string[];
  reason: string;
  category?: string;
}

export interface BatchDomainResult {
  success_count: number;
  failure_count: number;
  failed_domains: string[];
  message: string;
}

// 被阻止域名相关API
export const getBlockedDomains = async (skip: number = 0, limit: number = 100): Promise<Domain[]> => {
  return apiClient.get('/v1/domains/blocked', { params: { skip, limit } });
};

export const createBlockedDomain = async (data: CreateDomainData): Promise<Domain> => {
  return apiClient.post('/v1/domains/blocked', data);
};

export const createBlockedDomainsBatch = async (data: BatchDomainData): Promise<BatchDomainResult> => {
  return apiClient.post('/v1/domains/blocked/batch', data);
};

export const deleteBlockedDomain = async (id: number): Promise<void> => {
  return apiClient.delete(`/v1/domains/blocked/${id}`);
};

export const toggleBlockedDomain = async (id: number): Promise<Domain> => {
  return apiClient.put(`/v1/domains/blocked/${id}/toggle`);
};

// 白名单域名相关API
export const getWhitelistDomains = async (skip: number = 0, limit: number = 100): Promise<Domain[]> => {
  return apiClient.get('/v1/domains/whitelist', { params: { skip, limit } });
};

export const createWhitelistDomain = async (data: CreateDomainData): Promise<Domain> => {
  return apiClient.post('/v1/domains/whitelist', data);
};

export const deleteWhitelistDomain = async (id: number): Promise<void> => {
  return apiClient.delete(`/v1/domains/whitelist/${id}`);
};
