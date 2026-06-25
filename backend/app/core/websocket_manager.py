from typing import Set, Dict, Any
from fastapi import WebSocket
from app.core.logger import logger

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储所有活动的WebSocket连接
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """
        处理新的WebSocket连接
        
        Args:
            websocket: WebSocket连接实例
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        处理WebSocket连接断开
        
        Args:
            websocket: WebSocket连接实例
        """
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        向所有活动连接广播消息
        
        Args:
            message: 要广播的消息
        """
        if not self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket client: {str(e)}")
                disconnected.add(connection)
        
        # 移除断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        向特定WebSocket连接发送消息
        
        Args:
            message: 要发送的消息
            websocket: WebSocket连接实例
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {str(e)}")
            self.disconnect(websocket)

# 创建全局WebSocket管理器实例
websocket_manager = WebSocketManager()
