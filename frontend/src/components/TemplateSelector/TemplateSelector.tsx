import React, { useState, useMemo, useCallback } from 'react';
import { TemplateService, type Template } from '../../services/templateService';
import { t } from '../../i18n/i18n';
import './TemplateSelector.css';

interface TemplateSelectorProps {
  templates: Template[];
  selectedTemplate: string;
  onSelectTemplate: (templateId: string) => void;
  onClearTemplate: () => void;
  className?: string;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  templates,
  selectedTemplate,
  onSelectTemplate,
  onClearTemplate,
  className = ''
}) => {
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [previewMode, setPreviewMode] = useState<'thumbnail' | 'detail'>('thumbnail');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('popularity');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPreviewTemplate, setSelectedPreviewTemplate] = useState<Template | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  // 获取模板服务实例
  const templateService = TemplateService.getInstance();
  
  // 模板应用前验证
  const validateTemplateForApplication = useCallback((template: Template): { valid: boolean; error?: string } => {
    try {
      // 验证模板内容
      const contentString = JSON.stringify(template.content);
      const validationResult = templateService.validateTemplate(contentString);
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
      
      // 检查模板是否包含有效的内容
      const hasValidContent = template.content && (
        Array.isArray(template.content.domains) || 
        Array.isArray(template.content.allowedDomains) ||
        template.content.categories ||
        template.content.blockAllOthers !== undefined
      );
      
      if (!hasValidContent) {
        return {
          valid: false,
          error: t('templates.invalid_template')
        };
      }
      
      // 检查域名列表是否为空
      if (
        (Array.isArray(template.content.domains) && template.content.domains.length === 0) && 
        (Array.isArray(template.content.allowedDomains) && template.content.allowedDomains.length === 0) &&
        !template.content.categories &&
        template.content.blockAllOthers === undefined
      ) {
        return {
          valid: false,
          error: t('templates.template_domains_empty')
        };
      }
      
      return { valid: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        valid: false,
        error: `${t('templates.failed_to_apply')}: ${errorMessage}`
      };
    }
  }, [t, templateService]);

  // 获取当前语言
  const currentLanguage = window.localStorage.getItem('language') as 'en' | 'zh' || 'en';

  // 筛选和排序模板
  const filteredAndSortedTemplates = useMemo(() => {
    let result = [...templates];

    // 按类型筛选
    if (filterType !== 'all') {
      result = result.filter(template => {
        // 从模板内容中提取类型进行筛选
        if (filterType === 'block_list') {
          return template.content && template.content.domains && Array.isArray(template.content.domains) &&
                 (!template.content.allowedDomains || !Array.isArray(template.content.allowedDomains) || template.content.allowedDomains.length === 0);
        } else if (filterType === 'allow_list') {
          return template.content && template.content.allowedDomains && Array.isArray(template.content.allowedDomains);
        } else if (filterType === 'mixed') {
          return template.content && template.content.domains && Array.isArray(template.content.domains) &&
                 template.content.allowedDomains && Array.isArray(template.content.allowedDomains) &&
                 template.content.allowedDomains.length > 0;
        } else {
          return true;
        }
      });
    }

    // 按搜索词筛选
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(template => 
        template.name[currentLanguage]?.toLowerCase().includes(term) ||
        template.description[currentLanguage]?.toLowerCase().includes(term)
      );
    }

    // 排序
    switch (sortBy) {
      case 'name':
        result.sort((a, b) => a.name[currentLanguage]?.localeCompare(b.name[currentLanguage] || '') || 0);
        break;
      case 'popularity':
        // 基于创建时间模拟热度排序
        result.sort((a, b) => {
          const daysA = Math.floor((new Date().getTime() - new Date(a.createdAt).getTime()) / (1000 * 60 * 60 * 24));
          const daysB = Math.floor((new Date().getTime() - new Date(b.createdAt).getTime()) / (1000 * 60 * 60 * 24));
          return daysA - daysB; // 较新的模板排在前面
        });
        break;
      case 'recent':
        result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
        break;
      default:
        break;
    }

    return result;
  }, [templates, filterType, sortBy, searchTerm, currentLanguage]);

  // 应用模板
  const handleApplyTemplate = useCallback((templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (!template) return;
    
    // 模板应用前验证
    const validationResult = validateTemplateForApplication(template);
    if (!validationResult.valid) {
      setErrorMessage(validationResult.error || t('templates.invalid_template'));
      // 3秒后清除错误信息
      setTimeout(() => setErrorMessage(null), 3000);
      return;
    }
    
    // 验证通过，应用模板
    onSelectTemplate(templateId);
    setShowTemplateSelector(false);
    setErrorMessage(null);
  }, [onSelectTemplate, templates, validateTemplateForApplication, t]);

  // 显示模板预览
  const handlePreviewTemplate = useCallback((template: Template) => {
    setSelectedPreviewTemplate(template);
  }, []);

  // 关闭预览
  const handleClosePreview = useCallback(() => {
    setSelectedPreviewTemplate(null);
  }, []);

  // 切换模板选择器显示
  const toggleTemplateSelector = useCallback(() => {
    setShowTemplateSelector(prev => !prev);
  }, []);

  // 获取模板类型列表
  const templateTypes = useMemo(() => {
    // 从模板内容中提取类型，而不是直接使用template.type
    const types = new Set<string>(templates.map(template => {
      if (template.content && template.content.domains && Array.isArray(template.content.domains)) {
        if (template.content.allowedDomains && Array.isArray(template.content.allowedDomains)) {
          return 'mixed';
        }
        return 'block_list';
      }
      if (template.content && template.content.allowedDomains && Array.isArray(template.content.allowedDomains)) {
        return 'allow_list';
      }
      return 'custom';
    }));
    return ['all', ...types];
  }, [templates]);
  
  // 优化模板列表渲染，使用useMemo缓存渲染结果
  const renderedTemplates = useMemo(() => {
    return filteredAndSortedTemplates.map(template => {
      // 从模板内容中提取类型
      let templateType = 'custom';
      if (template.content && template.content.domains && Array.isArray(template.content.domains)) {
        if (template.content.allowedDomains && Array.isArray(template.content.allowedDomains)) {
          templateType = 'mixed';
        } else {
          templateType = 'block_list';
        }
      } else if (template.content && template.content.allowedDomains && Array.isArray(template.content.allowedDomains)) {
        templateType = 'allow_list';
      }
      
      // 模拟模板热度（基于创建时间）
      const createdDate = new Date(template.createdAt);
      const daysSinceCreated = Math.floor((new Date().getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24));
      const popularity = Math.max(0, 100 - daysSinceCreated);
      
      return (
        <div 
          key={template.id} 
          className={`template-item ${selectedTemplate === template.id ? 'selected' : ''}`}
          onClick={() => handleApplyTemplate(template.id)}
        >
          <div className="template-item-header">
            <h4>{template.name[currentLanguage]}</h4>
            <div className="template-meta">
              <span className="template-type-badge">{templateType}</span>
              <span className="template-popularity">
                <i className="icon-star"></i> {popularity}
              </span>
            </div>
          </div>
          <p className="template-description">{template.description[currentLanguage]}</p>
          <div className="template-actions">
            <button
              type="button"
              className="btn btn-small btn-preview"
              onClick={(e) => {
                e.stopPropagation();
                handlePreviewTemplate(template);
              }}
            >
              {t('templates.preview')}
            </button>
            <button
              type="button"
              className="btn btn-small btn-apply"
              onClick={(e) => {
                e.stopPropagation();
                handleApplyTemplate(template.id);
              }}
            >
              {t('templates.apply')}
            </button>
          </div>
        </div>
      );
    });
  }, [filteredAndSortedTemplates, selectedTemplate, currentLanguage, handleApplyTemplate, handlePreviewTemplate, t]);

  return (
    <div className={`template-selector ${className}`}>
      <div className="template-selector-header">
        <div className="template-selector-label-container">
          <label>{t('templates.select_template')}</label>
          <div className="tooltip-container">
            <i className="icon-help" title={t('templates.template_guide')}></i>
            <div className="tooltip-content">
              {t('templates.template_usage')}: {t('templates.guide_step_1')}<br />
              {t('templates.guide_step_2')}<br />
              {t('templates.guide_step_3')}
            </div>
          </div>
        </div>
        <div className="template-selector-actions">
          <button 
            type="button" 
            className="btn btn-secondary small"
            onClick={toggleTemplateSelector}
          >
            {showTemplateSelector ? t('templates.hide_templates') : t('templates.show_templates')}
          </button>
          {selectedTemplate && (
            <button 
              type="button" 
              className="btn btn-clear small"
              onClick={onClearTemplate}
            >
              {t('templates.clear_template')}
            </button>
          )}
        </div>
      </div>
      
      {/* 错误信息显示 */}
      {errorMessage && (
        <div className="template-error-message">
          <i className="icon-error"></i>
          {errorMessage}
        </div>
      )}
      
      {/* 模板选择器弹窗 */}
      {showTemplateSelector && (
        <div className="template-selector-modal">
          <div className="template-selector-content">
            {/* 搜索和筛选栏 */}
            <div className="template-selector-toolbar">
              <div className="search-box">
                <input
                  type="text"
                  placeholder={t('templates.search_templates')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="form-control"
                />
              </div>
              
              <div className="filter-sort-section">
                <div className="filter-group">
                  <label>{t('templates.filter_by')}:</label>
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="form-control small"
                  >
                    {templateTypes.map(type => (
                      <option key={type} value={type}>
                        {type === 'all' ? t('templates.all_types') : type}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>{t('templates.sort_by')}:</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="form-control small"
                  >
                    <option value="popularity">{t('templates.popularity')}</option>
                    <option value="name">{t('templates.name')}</option>
                    <option value="recent">{t('templates.recent')}</option>
                  </select>
                </div>
                
                <div className="filter-group">
                  <label>{t('templates.preview_mode')}:</label>
                  <div className="preview-mode-toggle">
                    <button
                      className={`mode-btn ${previewMode === 'thumbnail' ? 'active' : ''}`}
                      onClick={() => setPreviewMode('thumbnail')}
                    >
                      {t('templates.thumbnail')}
                    </button>
                    <button
                      className={`mode-btn ${previewMode === 'detail' ? 'active' : ''}`}
                      onClick={() => setPreviewMode('detail')}
                    >
                      {t('templates.detail')}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* 模板列表 */}
            <div className="template-list-container">
              {filteredAndSortedTemplates.length > 0 ? (
                <div className={`template-list ${previewMode}`}>
                  {renderedTemplates}
                </div>
              ) : (
                <div className="template-empty">
                  {t('templates.no_templates')}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* 模板预览模态框 */}
      {selectedPreviewTemplate && (
        <div className="template-preview-modal" onClick={handleClosePreview}>
          <div className="template-preview-content" onClick={(e) => e.stopPropagation()}>
            <div className="template-preview-header">
              <h3>{selectedPreviewTemplate.name[currentLanguage]}</h3>
              <button
                type="button"
                className="btn btn-close"
                onClick={handleClosePreview}
              >
                ×
              </button>
            </div>
            <div className="template-preview-body">
              <div className="template-preview-info">
                <p>{selectedPreviewTemplate.description[currentLanguage]}</p>
                <div className="template-preview-meta">
                  <span className="meta-item">
                    <strong>{t('templates.type')}:</strong> 
                    {(() => {
                      if (selectedPreviewTemplate.content && selectedPreviewTemplate.content.domains && Array.isArray(selectedPreviewTemplate.content.domains)) {
                        if (selectedPreviewTemplate.content.allowedDomains && Array.isArray(selectedPreviewTemplate.content.allowedDomains) && selectedPreviewTemplate.content.allowedDomains.length > 0) {
                          return 'mixed';
                        }
                        return 'block_list';
                      }
                      if (selectedPreviewTemplate.content && selectedPreviewTemplate.content.allowedDomains && Array.isArray(selectedPreviewTemplate.content.allowedDomains)) {
                        return 'allow_list';
                      }
                      return 'custom';
                    })()}
                  </span>
                  <span className="meta-item">
                    <strong>{t('templates.created')}:</strong> {new Date(selectedPreviewTemplate.createdAt).toLocaleDateString()}
                  </span>
                  <span className="meta-item">
                    <strong>{t('templates.source')}:</strong> {selectedPreviewTemplate.source}
                  </span>
                </div>
              </div>
              <div className="template-preview-content-area">
                <h4>{t('templates.content_preview')}</h4>
                <div className="template-content-display">
                  <pre>{JSON.stringify(selectedPreviewTemplate.content, null, 2)}</pre>
                </div>
              </div>
              <div className="template-preview-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleClosePreview}
                >
                  {t('templates.close')}
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => {
                    handleApplyTemplate(selectedPreviewTemplate.id);
                    handleClosePreview();
                  }}
                >
                  {t('templates.apply_template')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateSelector;