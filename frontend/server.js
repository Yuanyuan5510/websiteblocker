const http = require('http');
const fs = require('fs');
const path = require('path');
const httpProxy = require('http-proxy');

// 创建代理服务器
const proxy = httpProxy.createProxyServer({
  target: 'http://127.0.0.1:16411', // 后端服务器地址，使用127.0.0.1确保IPv4连接
  changeOrigin: true,
  secure: false
});

// 代理错误处理
proxy.on('error', (err, req, res) => {
  console.error('Proxy Error:', err);
  res.writeHead(500, { 'Content-Type': 'text/plain' });
  res.end('代理服务器错误: 无法连接到后端服务');
});

// 清理缓存函数
function clearCache() {
  try {
    // 定义可能的缓存目录
    const cacheDirs = [
      path.join(__dirname, '.cache'),
      path.join(__dirname, 'node_modules', '.cache')
    ];
    
    // 遍历并删除缓存目录
    cacheDirs.forEach(dir => {
      if (fs.existsSync(dir)) {
        console.log(`正在清理缓存目录: ${dir}`);
        // 删除目录及其内容
        deleteDirectory(dir);
      }
    });
    
    console.log('缓存清理完成');
  } catch (error) {
    console.error('缓存清理失败:', error.message);
  }
}

// 递归删除目录
function deleteDirectory(dirPath) {
  if (fs.existsSync(dirPath)) {
    fs.readdirSync(dirPath).forEach((file) => {
      const curPath = path.join(dirPath, file);
      if (fs.lstatSync(curPath).isDirectory()) {
        // 递归删除子目录
        deleteDirectory(curPath);
      } else {
        // 删除文件
        fs.unlinkSync(curPath);
      }
    });
    // 删除空目录
    fs.rmdirSync(dirPath);
  }
}

// 执行缓存清理
clearCache();

// 静态文件目录
// pkg 打包后需要使用正确的路径
let staticDir;
if (process.pkg) {
  // pkg 打包后的路径
  staticDir = path.join(path.dirname(process.execPath), 'dist');
} else {
  // 开发环境路径
  staticDir = path.join(__dirname, 'dist');
}
const port = 16410;

// MIME类型映射
const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// 创建HTTP服务器
const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // 处理关闭请求
  if (req.url === '/shutdown' && req.method === 'POST') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Shutting down server...');
    console.log('Received shutdown request, closing server...');
    
    // 优雅关闭服务器
    server.close(() => {
      console.log('Server closed gracefully');
      process.exit(0);
    });
    
    // 设置超时，确保服务器能正常关闭
    setTimeout(() => {
      console.log('Server shutdown timeout, force exit');
      process.exit(1);
    }, 5000);
    
    return;
  }

  // 解析请求路径
  let filePath = path.join(staticDir, req.url === '/' ? 'index.html' : req.url);
  
  // 获取文件扩展名
  const extname = path.extname(filePath);
  // 设置默认MIME类型
  const contentType = mimeTypes[extname] || 'application/octet-stream';

  // 读取文件
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 文件不存在，检查是否为API请求
        if (req.url.startsWith('/api/') || req.url === '/ws') {
          // API请求或WebSocket请求，转发到后端
          proxy.web(req, res);
        } else {
          // SPA路由，返回index.html
          const indexPath = path.join(staticDir, 'index.html');
          fs.readFile(indexPath, (indexErr, indexContent) => {
            if (indexErr) {
              res.writeHead(500);
              res.end(`Server Error: ${indexErr.code}`, 'utf-8');
            } else {
              res.writeHead(200, { 'Content-Type': 'text/html' });
              res.end(indexContent, 'utf-8');
            }
          });
        }
      } else {
        // 服务器错误
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`, 'utf-8');
      }
    } else {
      // 文件存在，返回文件内容
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

// 处理系统信号，支持外部关闭
process.on('SIGINT', () => {
  console.log('Received SIGINT, closing server...');
  server.close(() => {
    console.log('Server closed gracefully');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('Received SIGTERM, closing server...');
  server.close(() => {
    console.log('Server closed gracefully');
    process.exit(0);
  });
});

// 启动服务器
server.listen(port, () => {
  console.log(`前端应用已启动，访问地址: http://localhost:${port}`);
  console.log(`静态文件目录: ${staticDir}`);
  console.log('按 Ctrl+C 停止服务器');
});
