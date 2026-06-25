import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 直接返回响应数据
    return response.data;
  },
  (error) => {
    // 处理错误响应
    let errorMessage = 'API请求失败';
    
    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          errorMessage = `请求参数错误 (400): ${data.error?.message || 'Bad Request'}`;
          break;
        case 401:
          errorMessage = '未授权访问 (401)';
          break;
        case 403:
          errorMessage = '访问被拒绝 (403)';
          break;
        case 404:
          errorMessage = `请求的资源不存在 (404): ${error.config.url}`;
          break;
        case 405:
          errorMessage = `不支持的请求方法 (405): ${error.config.method?.toUpperCase()}`;
          break;
        case 422:
          errorMessage = `请求数据格式错误 (422): ${data.error?.message || 'Unprocessable Content'}`;
          break;
        case 500:
          errorMessage = `服务器内部错误 (500): ${data.error?.message || 'Internal Server Error'}`;
          break;
        default:
          errorMessage = `请求失败 (${status}): ${data.error?.message || 'Unknown Error'}`;
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMessage = '服务器无响应，请检查网络连接';
    } else {
      // 请求配置时发生错误
      errorMessage = `请求配置错误: ${error.message}`;
    }
    
    console.error('API Error:', errorMessage, error);
    
    // 在错误对象上添加自定义错误信息
    error.customMessage = errorMessage;
    
    return Promise.reject(error);
  }
);

export default apiClient;
