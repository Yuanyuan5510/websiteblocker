import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { t } from '../../i18n/i18n';
import { type Template, templateService } from '../../services/templateService';
import { createBlockedDomainsBatch } from '../../services/domainService';
import TemplateFormatter from '../TemplateFormatter/TemplateFormatter';
import './TemplateManager.css';

const TemplateManager: React.FC = () => {
  // 状态管理
  const [templates, setTemplates] = useState<Template[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // 主页面消息状态
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // 模态框消息状态（独立于主页面）
  const [modalError, setModalError] = useState<string | null>(null);
  const [modalSuccess, setModalSuccess] = useState<string | null>(null);
  
  // 模态框显示状态
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [helpTemplate, setHelpTemplate] = useState<Template | null>(null);
  
  // 模板应用引导状态
  const [showApplyGuide, setShowApplyGuide] = useState(false);
  const [guideStep, setGuideStep] = useState(1);
  
  // 添加模板表单状态
  const [newTemplate, setNewTemplate] = useState<{
    name: string;
    description: string;
    content: string;
  }>({
    name: '',
    description: '',
    content: ''
  });
  
  // 编辑模板表单状态
  const [editingTemplateData, setEditingTemplateData] = useState<{
    name: string;
    description: string;
    content: string;
  }>({
    name: '',
    description: '',
    content: ''
  });
  
  // 实时验证状态
  const [validationStatus, setValidationStatus] = useState<{ valid: boolean; error?: string }>({ valid: true });
  const [editValidationStatus, setEditValidationStatus] = useState<{ valid: boolean; error?: string }>({ valid: true });
  
  // 模板分类与筛选状态
  const [templateTypeFilter, setTemplateTypeFilter] = useState<string>('all'); // all, built-in, custom
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all'); // all, block-list, allow-list, mixed
  const [sortBy, setSortBy] = useState<string>('name'); // name, createdAt, updatedAt
  
  // 模板应用状态
  const [appliedTemplateId, setAppliedTemplateId] = useState<string | null>(null);
  
  // 获取模板类型
  const getTemplateType = useCallback((template: Template): 'block-list' | 'allow-list' | 'mixed' => {
    const content = template.content;
    const hasDomains = Array.isArray(content.domains) && content.domains.length > 0;
    const hasAllowedDomains = Array.isArray(content.allowedDomains) && content.allowedDomains.length > 0;
    
    if (hasDomains && hasAllowedDomains) {
      return 'mixed';
    } else if (hasDomains) {
      return 'block-list';
    } else if (hasAllowedDomains) {
      return 'allow-list';
    }
    return 'block-list';
  }, []);
  
  // 筛选和排序模板
  const filteredAndSortedTemplates = useMemo(() => {
    return templates.filter(template => {
      // 模板类型筛选
      const matchesType = templateTypeFilter === 'all' || 
        (templateTypeFilter === 'built-in' && template.isBuiltIn) ||
        (templateTypeFilter === 'custom' && !template.isBuiltIn);
      
      // 内容类型筛选
      const templateType = getTemplateType(template);
      const matchesContentType = contentTypeFilter === 'all' || contentTypeFilter === templateType;
      
      return matchesType && matchesContentType;
    }).sort((a, b) => {
      // 排序
      if (sortBy === 'name') {
        const lang = window.localStorage.getItem('language') as 'en' | 'zh' || 'en';
        return a.name[lang].localeCompare(b.name[lang]);
      } else if (sortBy === 'createdAt') {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      } else if (sortBy === 'updatedAt') {
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      }
      return 0;
    });
  }, [templates, templateTypeFilter, contentTypeFilter, sortBy, getTemplateType]);
  
  // 消息自动清除效果
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);
  
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);
  
  useEffect(() => {
    if (modalError) {
      const timer = setTimeout(() => setModalError(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [modalError]);
  
  useEffect(() => {
    if (modalSuccess) {
      const timer = setTimeout(() => setModalSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [modalSuccess]);
  
  // 清除消息
  const clearMessage = () => {
    setError(null);
    setSuccess(null);
  };
  
  // 清除模态框消息
  const clearModalMessage = () => {
    setModalError(null);
    setModalSuccess(null);
  };
  
  // 消息提示组件
  const Message = ({ type, message, onClear }: { type: 'error' | 'success'; message: string; onClear?: () => void }) => {
    return (
      <div className={`message ${type}`}>
        <span className="message-content">{message}</span>
        {onClear && (
          <button className="message-clear-btn" onClick={onClear}>
            ×
          </button>
        )}
      </div>
    );
  };

  // 获取模板列表
  const fetchTemplates = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // 从模板服务加载模板数据
      const templatesFromService = templateService.loadTemplates();
      setTemplates(templatesFromService);
    } catch (err) {
      setError('Failed to fetch templates');
      console.error('Failed to fetch templates:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchTemplates();
  }, []);

  // 处理文件上传
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = JSON.parse(event.target?.result as string);
        setNewTemplate(prev => ({
          ...prev,
          content: JSON.stringify(content, null, 2)
        }));
      } catch (err) {
        setError('Invalid JSON format');
      }
    };
    reader.readAsText(file);
  };

  // 添加模板
  const handleAddTemplate = async () => {
    const validationResult = templateService.validateTemplate(newTemplate.content);
    if (!validationResult.valid) {
      setModalError(validationResult.error || t('templates.invalid_json'));
      return;
    }

    setIsLoading(true);
    setModalError(null);
    setModalSuccess(null);

    try {
      // 使用模板服务添加模板
      templateService.addTemplate({
        name: {
          en: newTemplate.name,
          zh: newTemplate.name
        },
        description: {
          en: newTemplate.description,
          zh: newTemplate.description
        },
        isBuiltIn: false,
        content: JSON.parse(newTemplate.content),
        source: 'Custom'
      });

      // 更新模板列表
      setTemplates(templateService.getTemplates());
      setModalSuccess(t('templates.add_success'));
      
      // 延迟关闭模态框，让用户看到成功消息
      setTimeout(() => {
        setShowAddModal(false);
        setNewTemplate({
          name: '',
          description: '',
          content: ''
        });
        setModalSuccess(null);
      }, 1500);
    } catch (err) {
      setModalError(t('templates.add_error'));
      console.error('Failed to add template:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除模板
  const handleDeleteTemplate = async (id: string) => {
    const template = templates.find(t => t.id === id);
    if (!template) return;
    
    // 阻止内置模板被删除
    if (template.isBuiltIn) {
      setError(t('templates.built_in_cannot_be_deleted'));
      return;
    }
    
    if (!window.confirm(t('templates.delete_confirm'))) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const success = templateService.deleteTemplate(id);
      if (success) {
        setTemplates(templateService.getTemplates());
        setSuccess(t('templates.delete_success'));
      } else {
        setError(t('templates.delete_error'));
      }
    } catch (err) {
      setError(t('templates.delete_error'));
      console.error('Failed to delete template:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 批量删除模板
  const handleBatchDelete = async () => {
    if (selectedTemplates.length === 0) {
      setError(t('templates.select_at_least_one'));
      return;
    }

    // 检查是否包含内置模板
    const hasBuiltInTemplates = selectedTemplates.some(id => {
      const template = templates.find(t => t.id === id);
      return template?.isBuiltIn;
    });
    
    if (hasBuiltInTemplates) {
      setError(t('templates.built_in_cannot_be_deleted'));
      return;
    }

    if (!window.confirm(t('templates.batch_delete_confirm'))) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const deletedCount = templateService.batchDeleteTemplates(selectedTemplates);
      setTemplates(templateService.getTemplates());
      setSuccess(`${deletedCount} ${t('templates.template')}(s) ${t('templates.deleted_successfully')}`);
      setSelectedTemplates([]);
    } catch (err) {
      setError(t('templates.delete_error'));
      console.error('Failed to delete templates:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 恢复默认模板
  const handleRestoreDefaults = async () => {
    if (!window.confirm(t('templates.restore_confirm'))) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const restoredTemplates = templateService.restoreDefaultTemplates();
      setTemplates(restoredTemplates);
      setSuccess(t('templates.restore_success'));
    } catch (err) {
      setError(t('templates.restore_error'));
      console.error('Failed to restore default templates:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 切换模板选择
  const toggleTemplateSelection = useCallback((id: string) => {
    setSelectedTemplates(prev => {
      const newSelection = prev.includes(id) 
        ? prev.filter(selectedId => selectedId !== id)
        : [...prev, id];
      
      // 添加选择反馈
      if (newSelection.length > prev.length) {
        // 播放选择音效或显示短暂提示
        console.log(`Template ${id} selected`);
      }
      
      return newSelection;
    });
  }, []);
  
  // 模板卡片点击处理
  const handleTemplateCardClick = useCallback((template: Template) => {
    // 切换选中状态
    toggleTemplateSelection(template.id);
  }, [toggleTemplateSelection]);

  // 打开编辑模态框
  const handleOpenEditModal = useCallback((template: Template) => {
    const contentString = JSON.stringify(template.content, null, 2);
    setEditingTemplate(template);
    setEditingTemplateData({
      name: template.name[window.localStorage.getItem('language') as 'en' | 'zh'] || template.name.en,
      description: template.description[window.localStorage.getItem('language') as 'en' | 'zh'] || template.description.en,
      content: contentString
    });
    // 初始化验证状态
    setEditValidationStatus(templateService.validateTemplate(contentString));
    setShowEditModal(true);
  }, []);

  // 切换模板
  const handleSwitchTemplate = useCallback((templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      const contentString = JSON.stringify(template.content, null, 2);
      setEditingTemplate(template);
      setEditingTemplateData({
        name: template.name[window.localStorage.getItem('language') as 'en' | 'zh'] || template.name.en,
        description: template.description[window.localStorage.getItem('language') as 'en' | 'zh'] || template.description.en,
        content: contentString
      });
      // 更新验证状态
      setEditValidationStatus(templateService.validateTemplate(contentString));
    }
  }, [templates]);

  // 恢复模板到默认状态
  const handleRestoreTemplate = useCallback(() => {
    if (!editingTemplate) return;
    
    if (window.confirm(t('templates.restore_template_confirm'))) {
      // 使用模板服务恢复默认模板
      const restoredTemplate = templateService.restoreTemplateToDefault(editingTemplate.id);
      if (restoredTemplate) {
        const contentString = templateService.formatContent(restoredTemplate.content);
        setEditingTemplate(restoredTemplate);
        setEditingTemplateData({
          name: restoredTemplate.name[window.localStorage.getItem('language') as 'en' | 'zh'] || restoredTemplate.name.en,
          description: restoredTemplate.description[window.localStorage.getItem('language') as 'en' | 'zh'] || restoredTemplate.description.en,
          content: contentString
        });
        // 更新验证状态
        setEditValidationStatus(templateService.validateTemplate(contentString));
        // 更新模板列表
        setTemplates(templateService.getTemplates());
      }
    }
  }, [editingTemplate]);

  // 关闭编辑模态框
  const handleCloseEditModal = useCallback(() => {
    setShowEditModal(false);
    setEditingTemplate(null);
    setEditingTemplateData({
      name: '',
      description: '',
      content: ''
    });
    setEditValidationStatus({ valid: true });
  }, []);

  // 保存编辑后的模板
  const handleSaveEdit = useCallback(async () => {
    if (!editingTemplate) return;
    
    const validationResult = templateService.validateTemplate(editingTemplateData.content);
    if (!validationResult.valid) {
      setModalError(validationResult.error || t('templates.invalid_json'));
      return;
    }

    setIsLoading(true);
    setModalError(null);
    setModalSuccess(null);

    try {
      // 使用模板服务更新模板
      const updatedTemplate = templateService.updateTemplate(editingTemplate.id, {
        name: {
          en: editingTemplateData.name,
          zh: editingTemplateData.name
        },
        description: {
          en: editingTemplateData.description,
          zh: editingTemplateData.description
        },
        content: JSON.parse(editingTemplateData.content)
      });

      if (updatedTemplate) {
        setTemplates(templateService.getTemplates());
        setModalSuccess(t('templates.edit_success'));
        
        // 延迟关闭模态框，让用户看到成功消息
        setTimeout(() => {
          handleCloseEditModal();
          setModalSuccess(null);
        }, 1500);
      } else {
        setModalError(t('templates.edit_error'));
      }
    } catch (err) {
      setModalError(t('templates.edit_error'));
      console.error('Failed to update template:', err);
    } finally {
      setIsLoading(false);
    }
  }, [editingTemplate, editingTemplateData, handleCloseEditModal]);

  // 打开模板说明模态框
  const handleOpenHelpModal = useCallback((template: Template) => {
    setHelpTemplate(template);
    setShowHelpModal(true);
  }, []);
  
  // 关闭模板说明模态框
  const handleCloseHelpModal = useCallback(() => {
    setShowHelpModal(false);
    setHelpTemplate(null);
  }, []);
  
  // 关闭模板应用引导
  const closeApplyGuide = useCallback(() => {
    setShowApplyGuide(false);
    setGuideStep(1);
  }, []);
  
  // 下一步引导
  const nextGuideStep = useCallback(() => {
    setGuideStep(prev => prev + 1);
  }, []);
  
  // 上一步引导
  const prevGuideStep = useCallback(() => {
    setGuideStep(prev => prev - 1);
  }, []);
  
  // 模板应用完整性验证
  const validateTemplateForApplication = useCallback((template: Template): { valid: boolean; error?: string } => {
    // 验证模板内容
    const validationResult = templateService.validateTemplate(JSON.stringify(template.content));
    if (!validationResult.valid) {
      return validationResult;
    }
    
    // 检查模板内容是否为空
    if (!template.content || Object.keys(template.content).length === 0) {
      return {
        valid: false,
        error: t('templates.template_content_empty')
      };
    }
    
    // 检查模板是否包含有效的域名列表
    const content = template.content;
    if (!Array.isArray(content.domains) && !Array.isArray(content.allowedDomains)) {
      return {
        valid: false,
        error: t('templates.template_no_domains')
      };
    }
    
    // 检查域名列表是否为空
    if (Array.isArray(content.domains) && content.domains.length === 0 && 
        Array.isArray(content.allowedDomains) && content.allowedDomains.length === 0) {
      return {
        valid: false,
        error: t('templates.template_domains_empty')
      };
    }
    
    return { valid: true };
  }, []);
  
  // 模板应用功能
  const handleApplyTemplate = useCallback(async (template: Template) => {
    // 应用前验证
    const validationResult = validateTemplateForApplication(template);
    if (!validationResult.valid) {
      setError(validationResult.error || t('templates.invalid_template'));
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // 1. 使用模板服务保存应用记录
      templateService.applyTemplate(template.id);
      
      // 2. 从模板中提取域名列表
      const domainsToAdd: string[] = [];
      if (Array.isArray(template.content.domains)) {
        domainsToAdd.push(...template.content.domains);
      }
      
      if (domainsToAdd.length === 0) {
        setError(`${t('templates.failed_to_apply')}: ${t('templates.no_domains_to_apply')}`);
        return;
      }
      
      // 3. 使用批量API添加域名到阻止列表
      const templateName = template.name[window.localStorage.getItem('language') as 'en' | 'zh' || 'en'];
      const result = await createBlockedDomainsBatch({
        domains: domainsToAdd,
        reason: `模板应用: ${templateName}`,
        category: 'template'
      });
      
      // 4. 显示应用结果
      if (result.success_count > 0) {
        setAppliedTemplateId(template.id);
        let successMessage = `${t('templates.template')} "${templateName}" ${t('templates.applied_successfully')}`;
        successMessage += `\n${result.success_count} ${t('templates.domains_added_successfully')}`;
        if (result.failure_count > 0) {
          successMessage += `\n${result.failure_count} ${t('templates.domains_failed_to_add')}`;
        }
        setSuccess(successMessage);
        
        // 3秒后清除应用状态
        setTimeout(() => {
          setAppliedTemplateId(null);
        }, 3000);
      } else {
        // 所有域名添加失败
        setError(`${t('templates.failed_to_apply')} "${templateName}": ${t('templates.all_domains_failed_to_add')}`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(`${t('templates.failed_to_apply')} "${template.name[window.localStorage.getItem('language') as 'en' | 'zh' || 'en']}": ${errorMessage}`);
      console.error('Failed to apply template:', err);
    } finally {
      setIsLoading(false);
    }
  }, [validateTemplateForApplication]);
  
  // 渲染模板列表
  const renderTemplateList = () => {
    return filteredAndSortedTemplates.map(template => {
      const language = window.localStorage.getItem('language') as 'en' | 'zh' || 'en';
      const templateType = getTemplateType(template);
      const isApplied = appliedTemplateId === template.id;
      
      return (
        <div 
          key={template.id} 
          className={`template-card ${selectedTemplates.includes(template.id) ? 'selected' : ''}`}
          onClick={() => handleTemplateCardClick(template)}
        >
          <div className="template-header">
            <div className="template-info">
              <h3>{template.name[language]}</h3>
              <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {template.isBuiltIn && (
                  <span className="built-in-badge">
                    {t('templates.built_in')}
                  </span>
                )}
                <span className={`template-type-badge ${templateType}`}>
                  {templateType.replace('-', ' ').toUpperCase()}
                </span>
              </div>
            </div>
            <div className="template-checkbox">
              <input
                type="checkbox"
                checked={selectedTemplates.includes(template.id)}
                onChange={() => toggleTemplateSelection(template.id)}
                disabled={template.isBuiltIn}
              />
            </div>
          </div>
          
          <div className="template-content">
            <p className="template-description">{template.description[language]}</p>
            
            <div className="template-meta">
              <div><strong>{t('templates.source')}:</strong> {template.source}</div>
              <div><strong>{t('templates.type')}:</strong> {template.isBuiltIn ? t('templates.built_in') : t('templates.custom')}</div>
              <div><strong>{t('templates.created_at')}:</strong> {new Date(template.createdAt).toLocaleDateString()}</div>
              {template.updatedAt !== template.createdAt && (
                <div><strong>{t('templates.updated_at')}:</strong> {new Date(template.updatedAt).toLocaleDateString()}</div>
              )}
            </div>
            
            <div className="template-preview">
              <h4>{t('templates.preview')}:</h4>
              <TemplateFormatter content={template.content} compact={true} showLineNumbers={false} />
            </div>
          </div>
          
          <div className="template-actions-section">
            {isApplied ? (
              <div className="template-apply-success">
                {t('templates.applied_successfully')}
              </div>
            ) : (
              <button 
                className="template-apply-btn primary-btn"
                onClick={(e) => {
                  e.stopPropagation(); // 阻止事件冒泡
                  handleApplyTemplate(template);
                }}
                disabled={isLoading}
              >
                {t('templates.apply_template')}
              </button>
            )}
            
            <div className="template-secondary-actions">
              <button 
                className="btn btn-small btn-edit" 
                onClick={(e) => {
                  e.stopPropagation(); // 阻止事件冒泡
                  handleOpenEditModal(template);
                }}
              >
                {t('templates.edit')}
              </button>
              <button 
                className="btn btn-small btn-secondary" 
                onClick={(e) => {
                  e.stopPropagation(); // 阻止事件冒泡
                  handleOpenHelpModal(template);
                }}
              >
                {t('templates.view_details')}
              </button>
              <button 
                className="btn btn-small btn-delete" 
                onClick={(e) => {
                  e.stopPropagation(); // 阻止事件冒泡
                  handleDeleteTemplate(template.id);
                }}
                disabled={template.isBuiltIn}
              >
                {t('templates.delete')}
              </button>
            </div>
          </div>
        </div>
      );
    });
  };

  return (
    <div className="template-manager">
      {/* 主页面消息提示 - 固定在页面顶部 */}
      <div className="message-container">
        {error && <Message type="error" message={error} onClear={clearMessage} />}
        {success && <Message type="success" message={success} onClear={clearMessage} />}
      </div>
      
      <h2>{t('templates.template_manager')}</h2>
      
      <div className="template-actions">
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          {t('templates.add_template')}
        </button>
        <button className="btn btn-secondary" onClick={() => setShowImportModal(true)}>
          {t('templates.import_template')}
        </button>
        <button className="btn btn-danger" onClick={handleBatchDelete} disabled={selectedTemplates.length === 0}>
          {t('templates.batch_delete')}
        </button>
        <button className="btn btn-restore" onClick={handleRestoreDefaults}>
          {t('templates.restore_default')}
        </button>
      </div>

      {/* 模板筛选区域 */}
      <div style={{ 
        display: 'flex', 
        gap: '16px', 
        marginBottom: '24px', 
        flexWrap: 'wrap', 
        alignItems: 'center',
        background: 'linear-gradient(135deg, var(--surface-color) 0%, var(--background-color) 100%)',
        padding: '20px',
        borderRadius: '16px',
        boxShadow: 'var(--shadow-sm)',
        border: '1px solid var(--border-color)'
      }}>
        {/* 模板类型筛选 */}
        <div style={{ flex: '1 1 200px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: 600, 
            color: 'var(--text-primary)',
            fontSize: '14px' 
          }}>
            {t('templates.type')}
          </label>
          <select
            value={templateTypeFilter}
            onChange={(e) => setTemplateTypeFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: '12px',
              border: '2px solid var(--border-color)',
              fontSize: '14px',
              backgroundColor: 'var(--surface-color)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <option value="all">{t('templates.all')}</option>
            <option value="built-in">{t('templates.built_in')}</option>
            <option value="custom">{t('templates.custom')}</option>
          </select>
        </div>
        
        {/* 内容类型筛选 */}
        <div style={{ flex: '1 1 200px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: 600, 
            color: 'var(--text-primary)',
            fontSize: '14px' 
          }}>
            {t('templates.content_type')}
          </label>
          <select
            value={contentTypeFilter}
            onChange={(e) => setContentTypeFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: '12px',
              border: '2px solid var(--border-color)',
              fontSize: '14px',
              backgroundColor: 'var(--surface-color)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <option value="all">{t('templates.all')}</option>
            <option value="block-list">{t('templates.block_list')}</option>
            <option value="allow-list">{t('templates.allow_list')}</option>
            <option value="mixed">{t('templates.mixed')}</option>
          </select>
        </div>
        
        {/* 排序选项 */}
        <div style={{ flex: '1 1 200px' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '8px', 
            fontWeight: 600, 
            color: 'var(--text-primary)',
            fontSize: '14px' 
          }}>
            {t('templates.sort_by')}
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              borderRadius: '12px',
              border: '2px solid var(--border-color)',
              fontSize: '14px',
              backgroundColor: 'var(--surface-color)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <option value="name">{t('templates.name')}</option>
            <option value="createdAt">{t('templates.created_at')}</option>
            <option value="updatedAt">{t('templates.updated_at')}</option>
          </select>
        </div>
      </div>

      <div className="template-list">
        {isLoading ? (
          <div className="loading">{t('templates.loading')}</div>
        ) : filteredAndSortedTemplates.length === 0 ? (
          <div className="empty-state">
            {templateTypeFilter !== 'all' || contentTypeFilter !== 'all' ? 
              t('templates.no_matching_templates') : t('templates.no_templates')}
          </div>
        ) : (
          <>
            <div style={{ 
              marginBottom: '16px', 
              fontSize: '14px', 
              color: 'var(--text-secondary)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>{filteredAndSortedTemplates.length} {t('templates.templates_found')}</span>
              {selectedTemplates.length > 0 && (
                <span>{selectedTemplates.length} {t('templates.selected')}</span>
              )}
            </div>
            <div className="template-grid">
              {renderTemplateList()}
            </div>
          </>
        )}
      </div>

      {/* 添加模板模态框 */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-content">
              <h3>{t('templates.add_template')}</h3>
              
              {/* 模态框内消息提示 */}
              <div className="modal-messages">
                {modalError && <Message type="error" message={modalError} onClear={clearModalMessage} />}
                {modalSuccess && <Message type="success" message={modalSuccess} onClear={clearModalMessage} />}
              </div>
              
              <form onSubmit={(e) => { e.preventDefault(); handleAddTemplate(); }}>
                <div className="form-group">
                  <label>{t('templates.name')}:</label>
                  <input
                    type="text"
                    value={newTemplate.name}
                    onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('templates.description')}:</label>
                  <textarea
                    value={newTemplate.description}
                    onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <div className="form-group-header">
                    <label>{t('templates.content')}:</label>
                    <button 
                      type="button" 
                      className="btn btn-small btn-secondary" 
                      onClick={() => {
                        // 自动格式化JSON内容
                        try {
                          const parsed = JSON.parse(newTemplate.content);
                          const formatted = JSON.stringify(parsed, null, 2);
                          setNewTemplate({ ...newTemplate, content: formatted });
                          setValidationStatus(templateService.validateTemplate(formatted));
                        } catch (error) {
                          // 如果JSON无效，不执行格式化
                        }
                      }}
                    >
                      {t('templates.format_json')}
                    </button>
                  </div>
                  <div className="editor-container">
                    <textarea
                      className={validationStatus.valid ? '' : 'invalid'}
                      value={newTemplate.content}
                      onChange={(e) => {
                        setNewTemplate({ ...newTemplate, content: e.target.value });
                        setValidationStatus(templateService.validateTemplate(e.target.value));
                      }}
                      required
                      rows={15}
                      spellCheck={false}
                    />
                    {!validationStatus.valid && <div className="validation-error">{validationStatus.error}</div>}
                  </div>
                </div>
                <div className="form-group">
                  <label>{t('templates.import_from_file')}:</label>
                  <input type="file" accept=".json" onChange={handleFileUpload} />
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-cancel" onClick={() => {
                    setShowAddModal(false);
                    setNewTemplate({ name: '', description: '', content: '' });
                    setValidationStatus({ valid: true });
                  }}>
                    {t('templates.cancel')}
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={isLoading || !validationStatus.valid}>
                    {isLoading ? t('templates.saving') : t('templates.save')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* 导入模板模态框 */}
      {showImportModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-content">
              <h3>{t('templates.import_template')}</h3>
              <form>
                <div className="form-group">
                  <label>{t('templates.import_from_file')}:</label>
                  <input type="file" accept=".json" />
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-cancel" onClick={() => setShowImportModal(false)}>
                    {t('templates.cancel')}
                  </button>
                  <button type="button" className="btn btn-primary">
                    {t('templates.import')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* 编辑模板模态框 */}
      {showEditModal && editingTemplate && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-content edit-modal">
              <h3>{t('templates.edit_template')} - {editingTemplate.name[window.localStorage.getItem('language') as 'en' | 'zh' || 'en']}</h3>
              
              {/* 模态框内消息提示 */}
              <div className="modal-messages">
                {modalError && <Message type="error" message={modalError} onClear={clearModalMessage} />}
                {modalSuccess && <Message type="success" message={modalSuccess} onClear={clearModalMessage} />}
              </div>
              
              <div className="template-switcher">
                <label>{t('templates.switch_template')}:</label>
                <select onChange={(e) => handleSwitchTemplate(e.target.value)} value={editingTemplate.id}>
                  {templates.map(template => {
                    const language = window.localStorage.getItem('language') as 'en' | 'zh' || 'en';
                    return (
                      <option key={template.id} value={template.id}>
                        {template.name[language]}
                      </option>
                    );
                  })}
                </select>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleSaveEdit(); }}>
                <div className="form-group">
                  <label>{t('templates.name')}:</label>
                  <input
                    type="text"
                    value={editingTemplateData.name}
                    onChange={(e) => setEditingTemplateData({ ...editingTemplateData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>{t('templates.description')}:</label>
                  <textarea
                    value={editingTemplateData.description}
                    onChange={(e) => setEditingTemplateData({ ...editingTemplateData, description: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <div className="form-group-header">
                    <label>{t('templates.content')}:</label>
                    <button 
                      type="button" 
                      className="btn btn-small btn-secondary" 
                      onClick={() => {
                        // 自动格式化JSON内容
                        try {
                          const parsed = JSON.parse(editingTemplateData.content);
                          const formatted = JSON.stringify(parsed, null, 2);
                          setEditingTemplateData({ ...editingTemplateData, content: formatted });
                          setEditValidationStatus(templateService.validateTemplate(formatted));
                        } catch (error) {
                          // 如果JSON无效，不执行格式化
                        }
                      }}
                    >
                      {t('templates.format_json')}
                    </button>
                  </div>
                  <div className="editor-container">
                    <textarea
                      className={editValidationStatus.valid ? '' : 'invalid'}
                      value={editingTemplateData.content}
                      onChange={(e) => {
                        setEditingTemplateData({ ...editingTemplateData, content: e.target.value });
                        setEditValidationStatus(templateService.validateTemplate(e.target.value));
                      }}
                      required
                      rows={15}
                      spellCheck={false}
                    />
                    {!editValidationStatus.valid && <div className="validation-error">{editValidationStatus.error}</div>}
                  </div>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-cancel" onClick={handleCloseEditModal}>
                    {t('templates.cancel')}
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-restore" 
                    onClick={handleRestoreTemplate}
                    disabled={!editingTemplate?.isBuiltIn}
                  >
                    {t('templates.restore_default')}
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={isLoading || !editValidationStatus.valid}>
                    {isLoading ? t('templates.saving') : t('templates.save')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* 模板说明模态框 */}
      {showHelpModal && helpTemplate && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '800px' }}>
            <div className="modal-content">
              <h3>{t('templates.template_details')} - {helpTemplate.name[window.localStorage.getItem('language') as 'en' | 'zh' || 'en']}</h3>
              
              <div style={{ marginTop: '20px' }}>
                <h4>{t('templates.description')}:</h4>
                <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '20px' }}>
                  {helpTemplate.description[window.localStorage.getItem('language') as 'en' | 'zh' || 'en']}
                </p>
                
                <h4>{t('templates.template_usage')}:</h4>
                <div style={{ 
                  background: 'var(--background-color)', 
                  padding: '16px', 
                  borderRadius: '8px', 
                  marginBottom: '20px',
                  borderLeft: '4px solid var(--primary-color)'
                }}>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>Template ID:</strong> {helpTemplate.id}
                  </p>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>{t('templates.type')}:</strong> {helpTemplate.isBuiltIn ? t('templates.built_in') : t('templates.custom')}
                  </p>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>{t('templates.source')}:</strong> {helpTemplate.source}
                  </p>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>{t('templates.created_at')}:</strong> {new Date(helpTemplate.createdAt).toLocaleString()}
                  </p>
                  <p style={{ margin: '0' }}>
                    <strong>{t('templates.updated_at')}:</strong> {new Date(helpTemplate.updatedAt).toLocaleString()}
                  </p>
                </div>
                
                <h4>{t('templates.preview')}:</h4>
                <div style={{ marginBottom: '20px' }}>
                  <TemplateFormatter content={helpTemplate.content} compact={true} showLineNumbers={true} />
                </div>
                
                <h4>{t('templates.template_guide')}:</h4>
                <div style={{ 
                  background: 'var(--background-color)', 
                  padding: '16px', 
                  borderRadius: '8px',
                  borderLeft: '4px solid var(--secondary-color)'
                }}>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>{t('templates.applying_template')}:</strong> {t('templates.guide_step_2')}
                  </p>
                  <p style={{ margin: '0 0 12px 0' }}>
                    <strong>{t('templates.template_effect')}:</strong> {t('templates.guide_step_3')}
                  </p>
                  <p style={{ margin: '0' }}>
                    <strong>{t('templates.viewing_results')}:</strong> {t('templates.guide_step_4')}
                  </p>
                </div>
              </div>
              
              <div className="modal-actions">
                <button type="button" className="btn btn-primary" onClick={handleCloseHelpModal}>
                  {t('templates.close')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* 模板应用引导 */}
      {showApplyGuide && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '600px' }}>
            <div className="modal-content">
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '20px'
              }}>
                <h3>{t('templates.apply_guide')}</h3>
                <div style={{ 
                  background: 'var(--primary-color)', 
                  color: 'white', 
                  padding: '6px 12px', 
                  borderRadius: '20px', 
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {t('templates.step')} {guideStep} {t('templates.total_steps')} 4
                </div>
              </div>
              
              <div style={{ marginTop: '20px', textAlign: 'center', padding: '20px 0' }}>
                {guideStep === 1 && (
                  <div>
                    <div style={{ 
                      fontSize: '64px', 
                      marginBottom: '20px',
                      color: 'var(--primary-color)'
                    }}>
                      🔍
                    </div>
                    <h4>{t('templates.guide_step_1')}</h4>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
                      Browse through the template list and select the one that best fits your needs.
                    </p>
                  </div>
                )}
                
                {guideStep === 2 && (
                  <div>
                    <div style={{ 
                      fontSize: '64px', 
                      marginBottom: '20px',
                      color: 'var(--primary-color)'
                    }}>
                      🖱️
                    </div>
                    <h4>{t('templates.guide_step_2')}</h4>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
                      Click on the "Apply Template" button to apply the selected template to your system.
                    </p>
                  </div>
                )}
                
                {guideStep === 3 && (
                  <div>
                    <div style={{ 
                      fontSize: '64px', 
                      marginBottom: '20px',
                      color: 'var(--primary-color)'
                    }}>
                      ✅
                    </div>
                    <h4>{t('templates.guide_step_3')}</h4>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
                      The template will be applied to your system, and you will see a confirmation message.
                    </p>
                  </div>
                )}
                
                {guideStep === 4 && (
                  <div>
                    <div style={{ 
                      fontSize: '64px', 
                      marginBottom: '20px',
                      color: 'var(--primary-color)'
                    }}>
                      📊
                    </div>
                    <h4>{t('templates.guide_step_4')}</h4>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
                      You can view the results of the applied template in the main dashboard.
                    </p>
                  </div>
                )}
              </div>
              
              <div className="modal-actions" style={{ justifyContent: 'space-between' }}>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={prevGuideStep}
                  disabled={guideStep === 1}
                >
                  {t('templates.previous')}
                </button>
                
                {guideStep === 4 ? (
                  <button type="button" className="btn btn-primary" onClick={closeApplyGuide}>
                    {t('templates.close')}
                  </button>
                ) : (
                  <button type="button" className="btn btn-primary" onClick={nextGuideStep}>
                    {t('templates.next')}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateManager;
