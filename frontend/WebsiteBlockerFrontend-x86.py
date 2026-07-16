#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Blocker Frontend Service - 32-bit version
前端服务程序，用于提供静态文件服务和 API 反向代理

功能：
1. 提供前端静态文件服务（端口 16410）
2. 反向代理 API 请求到后端服务（端口 16411）
3. 支持 CORS 跨域请求
4. 支持 WebSocket 连接（如果需要）

Nuitka 打包说明：
- 使用 sys.argv[0] 获取可执行文件路径（Nuitka 推荐）
- 静态文件路径使用相对于可执行文件的路径
- 支持 .dist 目录检测（Nuitka 打包后的临时目录）
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, urljoin
import threading
import time

try:
    import requests
except ImportError:
    print("警告: requests 模块未安装，API 代理功能将不可用")
    print("请运行: pip install requests")
    requests = None


class FrontendHandler(SimpleHTTPRequestHandler):
    """前端请求处理器"""
    
    # 后端 API 地址
    BACKEND_URL = "http://127.0.0.1:16411"
    
    # 静态文件目录
    STATIC_DIR = None
    
    def __init__(self, *args, **kwargs):
        # 设置静态文件目录
        if FrontendHandler.STATIC_DIR is None:
            FrontendHandler.STATIC_DIR = get_static_dir()
        
        super().__init__(*args, directory=FrontendHandler.STATIC_DIR, **kwargs)
    
    def do_GET(self):
        """处理 GET 请求"""
        # API 请求转发到后端
        if self.path.startswith('/api/'):
            self.proxy_request('GET')
        else:
            # 静态文件请求
            super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path.startswith('/api/'):
            self.proxy_request('POST')
        else:
            self.send_error(405, "Method Not Allowed")
    
    def do_PUT(self):
        """处理 PUT 请求"""
        if self.path.startswith('/api/'):
            self.proxy_request('PUT')
        else:
            self.send_error(405, "Method Not Allowed")
    
    def do_DELETE(self):
        """处理 DELETE 请求"""
        if self.path.startswith('/api/'):
            self.proxy_request('DELETE')
        else:
            self.send_error(405, "Method Not Allowed")
    
    def do_PATCH(self):
        """处理 PATCH 请求"""
        if self.path.startswith('/api/'):
            self.proxy_request('PATCH')
        else:
            self.send_error(405, "Method Not Allowed")
    
    def proxy_request(self, method):
        """反向代理请求到后端"""
        if requests is None:
            self.send_error(500, "requests module not installed")
            return
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # 构建后端 URL
            backend_url = self.BACKEND_URL + self.path
            
            # 转发请求
            headers = dict(self.headers)
            headers['Host'] = '127.0.0.1:16411'
            
            response = requests.request(
                method=method,
                url=backend_url,
                data=body,
                headers=headers,
                timeout=30,
                allow_redirects=False
            )
            
            # 发送响应
            self.send_response(response.status_code)
            
            # 转发响应头
            for key, value in response.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                    self.send_header(key, value)
            
            # 添加 CORS 头
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            
            self.end_headers()
            self.wfile.write(response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"API 代理错误: {e}")
            self.send_error(502, f"Bad Gateway: {str(e)}")
        except Exception as e:
            print(f"处理请求时发生错误: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS 预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def end_headers(self):
        """添加 CORS 头到所有响应"""
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")


def get_executable_dir():
    """
    获取可执行文件所在目录
    Nuitka 打包后，sys.executable 可能指向 python.exe
    因此使用 sys.argv[0] 来获取可执行文件路径
    """
    # Nuitka 打包后的路径检测
    if getattr(sys, 'frozen', False):
        # Nuitka 打包后，优先使用 sys.argv[0]
        executable_path = os.path.abspath(sys.argv[0])
    else:
        # 开发环境
        executable_path = os.path.abspath(__file__)
    
    return os.path.dirname(executable_path)


def get_static_dir():
    """
    获取静态文件目录
    支持 Nuitka 打包后的 .dist 目录
    """
    base_dir = get_executable_dir()
    
    # 可能的静态文件目录
    possible_dirs = [
        os.path.join(base_dir, 'dist'),  # 正常情况
        os.path.join(base_dir, '.dist', 'dist'),  # Nuitka 打包后
        os.path.join(base_dir, '..', 'dist'),  # 相对路径
        base_dir,  # 当前目录
    ]
    
    # 查找存在的目录
    for static_dir in possible_dirs:
        if os.path.exists(static_dir):
            index_html = os.path.join(static_dir, 'index.html')
            if os.path.exists(index_html):
                print(f"静态文件目录: {static_dir}")
                return static_dir
    
    # 默认使用当前目录
    print(f"警告: 未找到静态文件目录，使用当前目录: {base_dir}")
    return base_dir


def check_backend_connection():
    """检查后端服务连接状态"""
    if requests is None:
        return False
    
    try:
        response = requests.get("http://127.0.0.1:16411/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """主函数"""
    # 配置
    HOST = '127.0.0.1'
    PORT = 16410
    BACKEND_PORT = 16411
    
    print("=" * 60)
    print("Website Blocker Frontend Service - 32-bit version")
    print("=" * 60)
    print(f"前端服务地址: http://{HOST}:{PORT}")
    print(f"后端 API 地址: http://{HOST}:{BACKEND_PORT}")
    print(f"静态文件目录: {get_static_dir()}")
    print("=" * 60)
    
    # 检查后端连接
    print("\n检查后端服务连接...")
    if check_backend_connection():
        print("✓ 后端服务连接正常")
    else:
        print("⚠ 警告: 无法连接到后端服务")
        print(f"  请确保后端服务正在运行在端口 {BACKEND_PORT}")
    
    print("\n按 Ctrl+C 停止服务...")
    print("=" * 60)
    
    # 创建 HTTP 服务器
    server = HTTPServer((HOST, PORT), FrontendHandler)
    
    try:
        # 启动服务器
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n收到停止信号，正在关闭服务器...")
        server.shutdown()
        print("服务器已停止")


if __name__ == '__main__':
    main()