import apiClient from './apiClient';

// 类型定义
export interface Schedule {
  id: number;
  name: string;
  description?: string;
  cron_expression: string;
  active: boolean;
  created_at: string;
  updated_at: string;
  task_type: string;
  params: any;
}

export interface CreateScheduleData {
  name: string;
  description?: string;
  cron_expression: string;
  active?: boolean;
  task_type: string;
  params: any;
}

export interface UpdateScheduleData {
  name?: string;
  description?: string;
  cron_expression?: string;
  active?: boolean;
  task_type?: string;
  params?: any;
}

// 调度器相关API
export const getSchedules = async (): Promise<Schedule[]> => {
  return apiClient.get('/v1/schedules');
};

export const getScheduleById = async (id: number): Promise<Schedule> => {
  return apiClient.get(`/v1/schedules/${id}`);
};

export const createSchedule = async (data: CreateScheduleData): Promise<Schedule> => {
  return apiClient.post('/v1/schedules', data);
};

export const updateSchedule = async (id: number, data: UpdateScheduleData): Promise<Schedule> => {
  return apiClient.put(`/v1/schedules/${id}`, data);
};

export const deleteSchedule = async (id: number): Promise<void> => {
  return apiClient.delete(`/v1/schedules/${id}`);
};

export const toggleSchedule = async (id: number): Promise<Schedule> => {
  return apiClient.post(`/v1/schedules/${id}/toggle`);
};
