import React, { useEffect } from 'react';
import './ErrorPage.css';

interface ErrorPageProps {
  errorCode: 400 | 403 | 404 | 500;
  errorMessage?: string;
  onBack?: () => void;
}

const ErrorPage: React.FC<ErrorPageProps> = ({ 
  errorCode, 
  errorMessage, 
  onBack 
}) => {
  // 根据错误码获取错误信息
  const getErrorInfo = () => {
    switch (errorCode) {
      case 400:
        return {
          title: 'Bad Request',
          description: 'The server could not understand the request due to invalid syntax.',
          suggestion: 'Please check your request and try again.',
          icon: '🔍'
        };
      case 403:
        return {
          title: 'Forbidden',
          description: 'You don\'t have permission to access this resource.',
          suggestion: 'Please check your permissions or contact the administrator.',
          icon: '🚫'
        };
      case 404:
        return {
          title: 'Not Found',
          description: 'The requested resource could not be found on this server.',
          suggestion: 'Please check the URL and try again.',
          icon: '❌'
        };
      case 500:
        return {
          title: 'Internal Server Error',
          description: 'The server encountered an unexpected condition that prevented it from fulfilling the request.',
          suggestion: 'Please try again later or contact the administrator.',
          icon: '🔥'
        };
      default:
        return {
          title: 'Unknown Error',
          description: 'An unexpected error occurred.',
          suggestion: 'Please try again later.',
          icon: '❓'
        };
    }
  };

  const errorInfo = getErrorInfo();

  // 确保页面默认语言为英文，默认主题为浅色主题
  useEffect(() => {
    // 检查是否已有语言和主题设置
    if (!localStorage.getItem('language')) {
      localStorage.setItem('language', 'en');
    }
    if (!localStorage.getItem('theme')) {
      localStorage.setItem('theme', 'light');
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }, []);

  return (
    <div className="error-page">
      <div className="error-container">
        {/* 错误图标动画 */}
        <div className={`error-icon ${errorCode}`}>
          <span className="icon">{errorInfo.icon}</span>
        </div>
        
        {/* 错误信息 */}
        <div className="error-content">
          <h1 className="error-code">{errorCode}</h1>
          <h2 className="error-title">{errorInfo.title}</h2>
          <p className="error-description">
            {errorMessage || errorInfo.description}
          </p>
          <div className="error-suggestion">
            <strong>What you can do:</strong>
            <p>{errorInfo.suggestion}</p>
          </div>
        </div>
        
        {/* 导航指引 */}
        <div className="error-actions">
          {onBack ? (
            <button className="btn btn-primary" onClick={onBack}>
              Go Back
            </button>
          ) : (
            <a href="/" className="btn btn-primary">
              Go to Homepage
            </a>
          )}
          <a href="/" className="btn btn-secondary">
            Contact Support
          </a>
        </div>
      </div>
      
      {/* 页脚 */}
      <footer className="error-footer">
        <p>© 2026 Website Access Restriction Tool v4.5</p>
      </footer>
    </div>
  );
};

export default ErrorPage;