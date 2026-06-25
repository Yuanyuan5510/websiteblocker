import React, { useState, useEffect } from 'react';
import { 
  getBlockedDomains, 
  createBlockedDomain, 
  deleteBlockedDomain, 
  toggleBlockedDomain,
  getWhitelistDomains,
  createWhitelistDomain,
  deleteWhitelistDomain,
  type Domain, 
  type CreateDomainData 
} from '../../services/domainService';
import { TemplateService, type Template } from '../../services/templateService';
import TemplateSelector from '../TemplateSelector/TemplateSelector';
import websocketService from '../../services/websocketService';
import { t } from '../../i18n/i18n';
import './DomainManager.css';

const DomainManager: React.FC = () => {
  // 状态管理
  const [activeTab, setActiveTab] = useState<'blocked' | 'whitelist'>('blocked');
  const [blockedDomains, setBlockedDomains] = useState<Domain[]>([]);
  const [whitelistDomains, setWhitelistDomains] = useState<Domain[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newDomain, setNewDomain] = useState<CreateDomainData>({ domain: '', reason: '', category: '' });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  // 模板相关状态
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  // 获取域名列表
  const fetchDomains = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      if (activeTab === 'blocked') {
        const domains = await getBlockedDomains(0, 100);
        setBlockedDomains(domains);
      } else {
        const domains = await getWhitelistDomains(0, 100);
        setWhitelistDomains(domains);
      }
    } catch (err) {
      setError(t('domains.fetch_error'));
      console.error('Failed to fetch domains:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 初始加载和标签切换时获取域名列表
  useEffect(() => {
    fetchDomains();
  }, [activeTab]);

  // 加载模板
  useEffect(() => {
    const templateService = TemplateService.getInstance();
    const templatesFromService = templateService.loadTemplates();
    setTemplates(templatesFromService);
  }, []);

  // 应用模板
  const applyTemplate = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      // 从模板内容中提取域名信息
      const templateContent = template.content;
      if (templateContent && templateContent.domains && Array.isArray(templateContent.domains)) {
        // 这里可以根据模板内容设置域名表单
        // 例如，设置第一个域名为模板中的第一个域名
        if (templateContent.domains.length > 0) {
          setNewDomain(prev => ({
            ...prev,
            domain: templateContent.domains[0],
            reason: template.description[window.localStorage.getItem('language') as 'en' | 'zh' || 'en'] || '',
            category: template.name[window.localStorage.getItem('language') as 'en' | 'zh' || 'en'] || ''
          }));
        }
      }
      setSelectedTemplate(templateId);
    }
  };

  // 添加WebSocket监听器，实时更新域名列表
  useEffect(() => {
    const handleDomainUpdate = () => {
      fetchDomains();
    };

    websocketService.on('domain_updated', handleDomainUpdate);

    return () => {
      websocketService.off('domain_updated', handleDomainUpdate);
    };
  }, []);

  // 解析和转换域名格式
  const parseDomain = (input: string): string => {
    let domain = input.trim();
    
    try {
      // 移除协议部分 (http://, https://, ftp:// 等)
      domain = domain.replace(/^(https?:\/\/|ftp:\/\/)?/i, '');
      
      // 移除路径和查询参数
      const pathIndex = domain.indexOf('/');
      if (pathIndex !== -1) {
        domain = domain.substring(0, pathIndex);
      }
      
      // 移除端口号
      const portIndex = domain.indexOf(':');
      if (portIndex !== -1) {
        // 检查是否有IPv6地址的冒号
        if (!domain.startsWith('[')) {
          domain = domain.substring(0, portIndex);
        }
      }
      
      // 移除 www. 前缀（如果存在）
      domain = domain.replace(/^www\./i, '');
      
      return domain;
    } catch (error) {
      console.error('域名解析错误:', error);
      return domain;
    }
  };

  // 添加域名
  const handleAddDomain = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // 解析和转换域名格式
      const parsedDomain = parseDomain(newDomain.domain);
      const domainData = { ...newDomain, domain: parsedDomain };
      
      if (activeTab === 'blocked') {
        await createBlockedDomain(domainData);
        setSuccess(t('domains.add_blocked_success'));
      } else {
        await createWhitelistDomain(domainData);
        setSuccess(t('domains.add_whitelist_success'));
      }
      
      // 重置表单并关闭模态框
      setNewDomain({ domain: '', reason: '', category: '' });
      setShowAddModal(false);
      
      // 刷新域名列表
      fetchDomains();
    } catch (err) {
      setError(t('domains.add_error'));
      console.error('Failed to add domain:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除域名
  const handleDeleteDomain = async (id: number) => {
    if (!window.confirm(t('domains.confirm_delete'))) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      if (activeTab === 'blocked') {
        await deleteBlockedDomain(id);
        setSuccess(t('domains.delete_blocked_success'));
        setBlockedDomains(blockedDomains.filter(domain => domain.id !== id));
      } else {
        await deleteWhitelistDomain(id);
        setSuccess(t('domains.delete_whitelist_success'));
        setWhitelistDomains(whitelistDomains.filter(domain => domain.id !== id));
      }
    } catch (err) {
      setError(t('domains.delete_error'));
      console.error('Failed to delete domain:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 切换被阻止域名状态
  const handleToggleBlockedDomain = async (id: number) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const updatedDomain = await toggleBlockedDomain(id);
      setSuccess(t('domains.toggle_success'));
      setBlockedDomains(blockedDomains.map(domain => 
        domain.id === id ? updatedDomain : domain
      ));
    } catch (err) {
      setError(t('domains.toggle_error'));
      console.error('Failed to toggle domain:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 渲染域名列表
  const renderDomainList = () => {
    const domains = activeTab === 'blocked' ? blockedDomains : whitelistDomains;
    
    if (isLoading) {
      return <div className="loading">{t('domains.loading')}</div>;
    }
    
    if (domains.length === 0) {
      return <div className="empty-state">{t('domains.empty')}</div>;
    }
    
    return (
      <table className="domain-table">
        <thead>
          <tr>
            <th>{t('domains.domain')}</th>
            <th>{t('domains.reason')}</th>
            {activeTab === 'blocked' && <th>{t('domains.category')}</th>}
            {activeTab === 'blocked' && <th>{t('domains.active')}</th>}
            <th>{t('domains.created_at')}</th>
            <th>{t('domains.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {domains.map(domain => (
            <tr key={domain.id}>
              <td>{domain.domain}</td>
              <td>{domain.reason || '-'}</td>
              {activeTab === 'blocked' && <td>{domain.category || '-'}</td>}
              {activeTab === 'blocked' && (
                <td>
                  <span className={`status-badge ${domain.active ? 'active' : 'inactive'}`}>
                    {domain.active ? t('domains.enabled') : t('domains.disabled')}
                  </span>
                </td>
              )}
              <td>{new Date(domain.created_at).toLocaleString()}</td>
              <td>
                <div className="action-buttons">
                  {activeTab === 'blocked' && (
                    <button 
                      className="btn btn-secondary"
                      onClick={() => handleToggleBlockedDomain(domain.id)}
                      disabled={isLoading}
                    >
                      {domain.active ? t('domains.disable') : t('domains.enable')}
                    </button>
                  )}
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleDeleteDomain(domain.id)}
                    disabled={isLoading}
                  >
                    {t('domains.delete')}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div className="domain-manager">
      <div className="domain-manager-header">
        <h2>{t('domains.title')}</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddModal(true)}
          disabled={isLoading}
        >
          {t('domains.add')}
        </button>
      </div>

      {/* 标签切换 */}
      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'blocked' ? 'active' : ''}`}
          onClick={() => setActiveTab('blocked')}
        >
          {t('domains.blocked')}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'whitelist' ? 'active' : ''}`}
          onClick={() => setActiveTab('whitelist')}
        >
          {t('domains.whitelist')}
        </button>
      </div>

      {/* 消息提示 */}
      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      {/* 域名列表 */}
      <div className="domain-list">
        {renderDomainList()}
      </div>

      {/* 添加域名模态框 */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{t('domains.add')} {activeTab === 'blocked' ? t('domains.blocked') : t('domains.whitelist')}</h3>
              <button 
                className="close-btn"
                onClick={() => setShowAddModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleAddDomain} className="modal-body">
              {/* 模板选择 */}
              <div className="form-group">
                <TemplateSelector
                  templates={templates}
                  selectedTemplate={selectedTemplate}
                  onSelectTemplate={applyTemplate}
                  onClearTemplate={() => setSelectedTemplate('')}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="domain">{t('domains.domain')}</label>
                <input
                  type="text"
                  id="domain"
                  value={newDomain.domain}
                  onChange={(e) => setNewDomain({ ...newDomain, domain: e.target.value })}
                  required
                  placeholder={t('domains.domain_placeholder')}
                />
              </div>
              <div className="form-group">
                <label htmlFor="reason">{t('domains.reason')}</label>
                <input
                  type="text"
                  id="reason"
                  value={newDomain.reason}
                  onChange={(e) => setNewDomain({ ...newDomain, reason: e.target.value })}
                  placeholder={t('domains.reason_placeholder')}
                />
              </div>
              {activeTab === 'blocked' && (
                <div className="form-group">
                  <label htmlFor="category">{t('domains.category')}</label>
                  <input
                    type="text"
                    id="category"
                    value={newDomain.category || ''}
                    onChange={(e) => setNewDomain({ ...newDomain, category: e.target.value })}
                    placeholder={t('domains.category_placeholder')}
                  />
                </div>
              )}
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setShowAddModal(false)}
                >
                  {t('domains.cancel')}
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? t('domains.adding') : t('domains.add')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DomainManager;
