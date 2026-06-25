import React, { useState } from 'react';
import './TemplateFormatter.css';

interface TemplateFormatterProps {
  content: any;
  compact?: boolean;
  showLineNumbers?: boolean;
}

const TemplateFormatter: React.FC<TemplateFormatterProps> = ({ 
  content, 
  compact = false, 
  showLineNumbers = false 
}) => {
  const [copied, setCopied] = useState(false);

  // 格式化JSON内容
  const formatJson = (data: any): string => {
    try {
      return JSON.stringify(data, null, compact ? 2 : 4);
    } catch (error) {
      return String(data);
    }
  };

  // 复制到剪贴板
  const copyToClipboard = () => {
    const jsonText = formatJson(content);
    navigator.clipboard.writeText(jsonText)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(err => {
        console.error('Failed to copy JSON:', err);
      });
  };

  // 高亮JSON语法
  const highlightJson = (json: string): React.ReactNode => {
    return json.split(/(?<=[:{}[\],])|(?=[:{}[\],])/) 
      .map((token, index) => {
        const trimmedToken = token.trim();
        if (!trimmedToken) return token;

        // 匹配关键字
        if (trimmedToken === '{' || trimmedToken === '}' || trimmedToken === '[' || trimmedToken === ']') {
          return <span key={index} className="json-bracket">{token}</span>;
        }
        if (trimmedToken === ':' || trimmedToken === ',') {
          return <span key={index} className="json-punctuation">{token}</span>;
        }
        // 匹配字符串
        if (trimmedToken.startsWith('"') && trimmedToken.endsWith('"')) {
          return <span key={index} className="json-string">{token}</span>;
        }
        // 匹配数字
        if (/^-?\d+(\.\d+)?$/.test(trimmedToken)) {
          return <span key={index} className="json-number">{token}</span>;
        }
        // 匹配布尔值
        if (trimmedToken === 'true' || trimmedToken === 'false') {
          return <span key={index} className="json-boolean">{token}</span>;
        }
        // 匹配null
        if (trimmedToken === 'null') {
          return <span key={index} className="json-null">{token}</span>;
        }
        return token;
      });
  };

  const formattedContent = formatJson(content);

  return (
    <div className={`template-formatter ${compact ? 'compact' : ''}`}>
      <button 
        className={`copy-button ${copied ? 'copied' : ''}`}
        onClick={copyToClipboard}
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
      <pre className="json-display">
        {showLineNumbers && (
          <div className="line-numbers">
            {formattedContent.split('\n').map((_, index) => (
              <div key={index} className="line-number">
                {index + 1}
              </div>
            ))}
          </div>
        )}
        <code className="json-content">
          {highlightJson(formattedContent)}
        </code>
      </pre>
    </div>
  );
};

export default TemplateFormatter;