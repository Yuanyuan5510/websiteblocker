import React, { useState, useEffect } from 'react';
import { getHostsContent, updateHostsContent, reloadHosts } from '../../services/hostsService';
import { t } from '../../i18n/i18n';
import './HostsManager.css';

const HostsManager: React.FC = () => {
  // 状态管理
  const [hostsContent, setHostsContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // 获取Hosts文件内容
  const fetchHostsContent = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await getHostsContent();
      setHostsContent(response.content);
    } catch (err) {
      setError(t('hosts.fetch_error'));
      console.error('Failed to fetch hosts content:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchHostsContent();
  }, []);

  // 保存Hosts文件
  const handleSaveHosts = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await updateHostsContent(hostsContent);
      setSuccess(t('hosts.save_success'));
      setIsEditing(false);
    } catch (err) {
      setError(t('hosts.save_error'));
      console.error('Failed to save hosts content:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 重新加载Hosts文件
  const handleReloadHosts = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await reloadHosts();
      setSuccess(t('hosts.reload_success'));
      // 重新获取Hosts文件内容
      await fetchHostsContent();
    } catch (err) {
      setError(t('hosts.reload_error'));
      console.error('Failed to reload hosts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 取消编辑
  const handleCancelEdit = () => {
    setIsEditing(false);
    // 重新获取原始内容
    fetchHostsContent();
  };

  return (
    <div className="hosts-manager">
      <div className="hosts-manager-header">
        <h2>{t('hosts.title')}</h2>
        <div className="action-buttons">
          {!isEditing ? (
            <button 
              className="btn btn-primary"
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
            >
              {t('hosts.edit')}
            </button>
          ) : (
            <>
              <button 
                className="btn btn-primary"
                onClick={handleSaveHosts}
                disabled={isLoading}
              >
                {isLoading ? t('hosts.save_loading') : t('hosts.save')}
              </button>
              <button 
                className="btn btn-secondary"
                onClick={handleCancelEdit}
                disabled={isLoading}
              >
                {t('hosts.cancel')}
              </button>
            </>
          )}
          <button 
            className="btn btn-secondary"
            onClick={handleReloadHosts}
            disabled={isLoading}
          >
            {t('hosts.reload')}
          </button>
        </div>
      </div>

      {/* 消息提示 */}
      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      {/* Hosts文件内容 */}
      <div className="hosts-content-container">
        {isLoading && !isEditing ? (
          <div className="loading">{t('hosts.loading')}</div>
        ) : (
          <div className="hosts-content">
            {isEditing ? (
              <textarea
                value={hostsContent}
                onChange={(e) => setHostsContent(e.target.value)}
                placeholder={t('hosts.content_placeholder')}
                className="hosts-textarea"
                spellCheck={false}
              />
            ) : (
              <pre className="hosts-pre">{hostsContent}</pre>
            )}
          </div>
        )}
      </div>

      {/* 操作说明 */}
      <div className="hosts-info">
        <h3>{t('hosts.info_title')}</h3>
        <ul>
          <li>{t('hosts.info_point_1')}</li>
          <li>{t('hosts.info_point_2')}</li>
          <li>{t('hosts.info_point_3')}</li>
          <li>{t('hosts.info_point_4')}</li>
          <li>{t('hosts.info_point_5')}</li>
        </ul>
      </div>
    </div>
  );
};

export default HostsManager;
