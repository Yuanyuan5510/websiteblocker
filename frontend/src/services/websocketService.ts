// WebSocket服务，用于处理实时更新

interface WebSocketMessage {
  type: string;
  action?: string;
  domain_type?: string;
  domain?: string;
  active?: boolean;
  timestamp?: string;
  message?: string;
  version?: string;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: Map<string, ((message: WebSocketMessage) => void)[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private url: string;
  private isConnecting = false;
  private isConnected = false;

  constructor(url: string = '') {
    // 如果没有提供URL，使用固定的后端WebSocket端点
    if (!url) {
      this.url = 'ws://localhost:8000/ws';
    } else {
      this.url = url;
    }
  }

  // 连接WebSocket服务器
  connect(): void {
    // 避免重复连接
    if (this.isConnected || this.isConnecting) {
      console.log('WebSocket已连接或正在连接中，避免重复连接');
      return;
    }

    try {
      this.isConnecting = true;
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket连接已关闭:', event.code, event.reason);
        this.isConnected = false;
        this.isConnecting = false;
        this.socket = null;
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      this.isConnecting = false;
      this.attemptReconnect();
    }
  }

  // 尝试重新连接
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重新连接WebSocket... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1));
    } else {
      console.error('WebSocket重连失败，已达到最大尝试次数');
    }
  }

  // 处理WebSocket消息
  private handleMessage(message: WebSocketMessage): void {
    // 只在开发环境下打印消息日志
    if (import.meta.env.MODE === 'development') {
      // 避免重复打印连接成功消息
      if (message.type !== 'connection_established') {
        console.log('收到WebSocket消息:', message);
      }
    }
    
    // 调用所有监听器
    const typeListeners = this.listeners.get(message.type) || [];
    typeListeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('处理WebSocket消息失败:', error);
      }
    });
    
    // 调用所有类型的监听器（用于全局监听）
    const allListeners = this.listeners.get('*') || [];
    allListeners.forEach(listener => {
      try {
        listener(message);
      } catch (error) {
        console.error('处理WebSocket消息失败:', error);
      }
    });
  }

  // 发送消息
  send(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }

  // 注册消息监听器
  on(type: string, callback: (message: WebSocketMessage) => void): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)?.push(callback);
  }

  // 取消消息监听器
  off(type: string, callback: (message: WebSocketMessage) => void): void {
    const typeListeners = this.listeners.get(type);
    if (typeListeners) {
      this.listeners.set(
        type,
        typeListeners.filter(listener => listener !== callback)
      );
    }
  }

  // 关闭WebSocket连接
  close(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      this.isConnecting = false;
    }
  }

  // 获取连接状态
  get readyState(): number | null {
    return this.socket?.readyState || null;
  }

  // 检查是否已连接
  getConnectionStatus(): boolean {
    return this.isConnected;
  }
}

// 创建WebSocket服务实例
const websocketService = new WebSocketService();

export default websocketService;
export type { WebSocketMessage };
