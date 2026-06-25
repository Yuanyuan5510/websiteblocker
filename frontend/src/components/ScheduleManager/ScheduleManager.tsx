import React, { useState, useEffect } from 'react';
import { 
  getSchedules, 
  createSchedule, 
  updateSchedule, 
  deleteSchedule, 
  toggleSchedule,
  type Schedule, 
  type CreateScheduleData,
  type UpdateScheduleData
} from '../../services/scheduleService';
import { getBlockedDomains } from '../../services/domainService';
import { TemplateService, type Template } from '../../services/templateService';
import TemplateSelector from '../TemplateSelector/TemplateSelector';
import { t } from '../../i18n/i18n';
import './ScheduleManager.css';

// 常用时间模板
const timeTemplates = [
  { name: '每天午夜', cron: '0 0 * * *' },
  { name: '每天早上9点', cron: '0 9 * * *' },
  { name: '每天下午6点', cron: '0 18 * * *' },
  { name: '每周一早上9点', cron: '0 9 * * 1' },
  { name: '工作日早上9点', cron: '0 9 * * 1-5' },
  { name: '每小时', cron: '0 * * * *' },
  { name: '每15分钟', cron: '*/15 * * * *' },
  { name: '每周日午夜', cron: '0 0 * * 0' },
  { name: '每月1号午夜', cron: '0 0 1 * *' },
  { name: '每天中午12点', cron: '0 12 * * *' }
];

// 时间字段类型
interface CronFields {
  minute: string;
  hour: string;
  day: string;
  month: string;
  dayOfWeek: string;
}

// 解析Cron表达式为时间字段
const parseCronExpression = (cron: string): CronFields => {
  const parts = cron.split(' ');
  return {
    minute: parts[0] || '*',
    hour: parts[1] || '*',
    day: parts[2] || '*',
    month: parts[3] || '*',
    dayOfWeek: parts[4] || '*'
  };
};

// 生成Cron表达式
const generateCronExpression = (fields: CronFields): string => {
  return `${fields.minute} ${fields.hour} ${fields.day} ${fields.month} ${fields.dayOfWeek}`;
};

// 解释Cron表达式
const explainCronExpression = (cron: string): string => {
  const fields = parseCronExpression(cron);
  let explanation = '在';
  
  // 小时和分钟
  if (fields.hour === '*' && fields.minute === '*') {
    explanation += '每分钟';
  } else if (fields.hour === '*') {
    explanation += `每小时的第 ${fields.minute} 分钟`;
  } else if (fields.minute === '*') {
    explanation += `每天 ${fields.hour}:00`;
  } else {
    explanation += `每天 ${fields.hour}:${fields.minute.padStart(2, '0')}`;
  }
  
  // 月份
  if (fields.month !== '*') {
    explanation += `，${fields.month}月`;
  }
  
  // 日期
  if (fields.day !== '*') {
    explanation += `的第 ${fields.day} 天`;
  }
  
  // 星期
  if (fields.dayOfWeek !== '*') {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    if (fields.dayOfWeek.includes('-')) {
      const [start, end] = fields.dayOfWeek.split('-');
      explanation += `，从${weekdays[parseInt(start)]}到${weekdays[parseInt(end)]}`;
    } else {
      explanation += `，${weekdays[parseInt(fields.dayOfWeek)]}`;
    }
  }
  
  explanation += '执行';
  return explanation;
};

const ScheduleManager: React.FC = () => {
  // 状态管理
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [currentSchedule, setCurrentSchedule] = useState<Schedule | null>(null);
  const [newSchedule, setNewSchedule] = useState<CreateScheduleData>({ 
    name: '', 
    description: '', 
    cron_expression: '', 
    active: true, 
    task_type: 'block',
    params: { domains: [] }
  });
  const [cronFields, setCronFields] = useState<CronFields>({
    minute: '*',
    hour: '*',
    day: '*',
    month: '*',
    dayOfWeek: '*'
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [domains, setDomains] = useState<string[]>([]);
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [taskType, setTaskType] = useState<string>('block');
  // 模板相关状态
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [cronExplanation, setCronExplanation] = useState<string>('');

  // 获取调度任务列表
  const fetchSchedules = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const scheduleList = await getSchedules();
      setSchedules(scheduleList);
    } catch (err) {
      setError(t('schedules.fetch_error'));
      console.error('Failed to fetch schedules:', err);
    } finally {
      setIsLoading(false);
    }
  };

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
        // 将模板中的域名添加到选择的域名列表中
        setSelectedDomains(templateContent.domains);
        // 更新调度任务的名称和描述
        const language = window.localStorage.getItem('language') as 'en' | 'zh' || 'en';
        setNewSchedule(prev => ({
          ...prev,
          name: template.name[language] || '',
          description: template.description[language] || ''
        }));
      }
      setSelectedTemplate(templateId);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchSchedules();
    fetchDomains();
  }, []);

  // 获取域名列表
  const fetchDomains = async () => {
    try {
      const blockedDomains = await getBlockedDomains();
      // 提取域名并去重
      const uniqueDomains = [...new Set(blockedDomains.map(domain => domain.domain))];
      setDomains(uniqueDomains);
    } catch (error) {
      console.error('获取域名列表失败:', error);
    }
  };

  // 添加调度任务
  const handleAddSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // 准备调度任务数据
      const scheduleData: CreateScheduleData = {
        ...newSchedule,
        task_type: taskType,
        params: {
          domains: selectedDomains
        }
      };
      
      await createSchedule(scheduleData);
      setSuccess('调度任务添加成功');
      // 重置表单并关闭模态框
      setNewSchedule({ name: '', description: '', cron_expression: '', active: true, task_type: 'block', params: { domains: [] } });
      setSelectedDomains([]);
      setTaskType('block');
      setShowAddModal(false);
      // 刷新列表
      await fetchSchedules();
    } catch (err) {
      setError('添加调度任务失败');
      console.error('Failed to add schedule:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 更新调度任务
  const handleUpdateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentSchedule) return;
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const updateData: UpdateScheduleData = {
        name: newSchedule.name,
        description: newSchedule.description,
        cron_expression: newSchedule.cron_expression,
        active: newSchedule.active,
        task_type: taskType,
        params: {
          domains: selectedDomains
        }
      };
      
      await updateSchedule(currentSchedule.id, updateData);
      setSuccess('调度任务更新成功');
      // 关闭模态框
      setShowEditModal(false);
      setCurrentSchedule(null);
      setSelectedDomains([]);
      setTaskType('block');
      // 刷新列表
      await fetchSchedules();
    } catch (err) {
      setError('更新调度任务失败');
      console.error('Failed to update schedule:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除调度任务
  const handleDeleteSchedule = async (id: number) => {
    if (!window.confirm('确定要删除这个调度任务吗？')) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      await deleteSchedule(id);
      setSuccess('调度任务删除成功');
      // 刷新列表
      await fetchSchedules();
    } catch (err) {
      setError('删除调度任务失败');
      console.error('Failed to delete schedule:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 切换调度任务状态
  const handleToggleSchedule = async (id: number) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const updatedSchedule = await toggleSchedule(id);
      setSuccess(`调度任务 ${updatedSchedule.name} 状态已更新`);
      // 更新列表中的任务状态
      setSchedules(schedules.map(schedule => 
        schedule.id === id ? updatedSchedule : schedule
      ));
    } catch (err) {
      setError('切换调度任务状态失败');
      console.error('Failed to toggle schedule:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 打开编辑模态框
  const handleOpenEditModal = (schedule: Schedule) => {
    setCurrentSchedule(schedule);
    setNewSchedule({
      name: schedule.name,
      description: schedule.description || '',
      cron_expression: schedule.cron_expression,
      active: schedule.active,
      task_type: schedule.task_type,
      params: schedule.params
    });
    setSelectedDomains(schedule.params?.domains || []);
    setTaskType(schedule.task_type);
    setShowEditModal(true);
  };

  // 关闭编辑模态框
  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setCurrentSchedule(null);
    setNewSchedule({ name: '', description: '', cron_expression: '', active: true, task_type: 'block', params: { domains: [] } });
    setCronFields({ minute: '*', hour: '*', day: '*', month: '*', dayOfWeek: '*' });
    setSelectedDomains([]);
    setTaskType('block');
  };

  // 使用时间模板
  const useTimeTemplate = (template: typeof timeTemplates[0]) => {
    setCronFields(parseCronExpression(template.cron));
    updateCronExpression(parseCronExpression(template.cron));
  };

  // 更新Cron表达式
  const updateCronExpression = (fields: CronFields) => {
    const cron = generateCronExpression(fields);
    setNewSchedule(prev => ({ ...prev, cron_expression: cron }));
    setCronExplanation(explainCronExpression(cron));
  };

  // 处理单个时间字段变化
  const handleCronFieldChange = (field: keyof CronFields, value: string) => {
    const newFields = { ...cronFields, [field]: value };
    setCronFields(newFields);
    updateCronExpression(newFields);
  };

  // 渲染调度任务列表
  const renderScheduleList = () => {
    if (isLoading) {
      return <div className="loading">加载中...</div>;
    }
    
    if (schedules.length === 0) {
      return <div className="empty-state">暂无调度任务</div>;
    }
    
    return (
      <table className="schedule-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>描述</th>
            <th>Cron表达式</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {schedules.map(schedule => (
            <tr key={schedule.id}>
              <td>{schedule.name}</td>
              <td>{schedule.description || '-'}</td>
              <td>{schedule.cron_expression}</td>
              <td>
                <span className={`status-badge ${schedule.active ? 'active' : 'inactive'}`}>
                  {schedule.active ? '已启用' : '已禁用'}
                </span>
              </td>
              <td>{new Date(schedule.created_at).toLocaleString()}</td>
              <td>{new Date(schedule.updated_at).toLocaleString()}</td>
              <td>
                <div className="action-buttons">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => handleToggleSchedule(schedule.id)}
                    disabled={isLoading}
                  >
                    {schedule.active ? '禁用' : '启用'}
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleOpenEditModal(schedule)}
                    disabled={isLoading}
                  >
                    编辑
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleDeleteSchedule(schedule.id)}
                    disabled={isLoading}
                  >
                    删除
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
    <div className="schedule-manager">
      <div className="schedule-manager-header">
        <h2>{t('schedules.title')}</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddModal(true)}
          disabled={isLoading}
        >
          {t('schedules.add')}
        </button>
      </div>

      {/* 消息提示 */}
      {error && <div className="message error">{error}</div>}
      {success && <div className="message success">{success}</div>}

      {/* 调度任务列表 */}
      <div className="schedule-list">
        {renderScheduleList()}
      </div>

      {/* 添加调度任务模态框 */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{t('schedules.add')}</h3>
              <button 
                className="close-btn"
                onClick={() => setShowAddModal(false)}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleAddSchedule} className="modal-body">
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
                <label htmlFor="name">{t('schedules.name')} <span className="required">*</span></label>
                <input
                  type="text"
                  id="name"
                  value={newSchedule.name}
                  onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
                  required
                  placeholder={t('schedules.name_placeholder')}
                />
              </div>
              <div className="form-group">
                <label htmlFor="task-type">{t('schedules.action')} <span className="required">*</span></label>
                <select
                  id="task-type"
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                >
                  <option value="block">{t('domains.block')}</option>
                  <option value="unblock">{t('domains.unblock')}</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="domains">{t('domains.domain')} <span className="required">*</span></label>
                <div className="domain-selector">
                  {domains.length === 0 ? (
                    <div className="empty-domains">{t('schedules.no_domains_available')}</div>
                  ) : (
                    <div className="domain-list">
                      {domains.map((domain) => (
                        <div key={domain} className="domain-item">
                          <input
                            type="checkbox"
                            id={`domain-${domain}`}
                            checked={selectedDomains.includes(domain)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDomains([...selectedDomains, domain]);
                              } else {
                                setSelectedDomains(selectedDomains.filter(d => d !== domain));
                              }
                            }}
                          />
                          <label htmlFor={`domain-${domain}`}>{domain}</label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="description">{t('schedules.description')}</label>
                <textarea
                  id="description"
                  value={newSchedule.description || ''}
                  onChange={(e) => setNewSchedule({ ...newSchedule, description: e.target.value })}
                  placeholder={t('schedules.description_placeholder')}
                  rows={3}
                />
              </div>
              {/* 常用时间模板 */}
              <div className="form-group">
                <label>{t('schedules.time_templates')}</label>
                <div className="time-templates">
                  {timeTemplates.map((template, index) => (
                    <button
                      key={index}
                      type="button"
                      className="btn btn-sm btn-secondary"
                      onClick={() => useTimeTemplate(template)}
                    >
                      {template.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* 可视化时间选择器 */}
              <div className="form-group">
                <label>{t('schedules.time_settings')}</label>
                <div className="cron-visualizer">
                  <div className="cron-field">
                    <label htmlFor="minute">{t('schedules.minute')}</label>
                    <input
                      type="text"
                      id="minute"
                      value={cronFields.minute}
                      onChange={(e) => handleCronFieldChange('minute', e.target.value)}
                      placeholder="*"
                    />
                  </div>
                  <div className="cron-field">
                    <label htmlFor="hour">{t('schedules.hour')}</label>
                    <input
                      type="text"
                      id="hour"
                      value={cronFields.hour}
                      onChange={(e) => handleCronFieldChange('hour', e.target.value)}
                      placeholder="*"
                    />
                  </div>
                  <div className="cron-field">
                    <label htmlFor="day">{t('schedules.day')}</label>
                    <input
                      type="text"
                      id="day"
                      value={cronFields.day}
                      onChange={(e) => handleCronFieldChange('day', e.target.value)}
                      placeholder="*"
                    />
                  </div>
                  <div className="cron-field">
                    <label htmlFor="month">{t('schedules.month')}</label>
                    <input
                      type="text"
                      id="month"
                      value={cronFields.month}
                      onChange={(e) => handleCronFieldChange('month', e.target.value)}
                      placeholder="*"
                    />
                  </div>
                  <div className="cron-field">
                    <label htmlFor="dayOfWeek">{t('schedules.dayOfWeek')}</label>
                    <input
                      type="text"
                      id="dayOfWeek"
                      value={cronFields.dayOfWeek}
                      onChange={(e) => handleCronFieldChange('dayOfWeek', e.target.value)}
                      placeholder="*"
                    />
                  </div>
                </div>
              </div>

              {/* Cron表达式显示和编辑 */}
              <div className="form-group">
                <label htmlFor="cron_expression">
                  {t('schedules.cron_expression')} <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="cron_expression"
                  value={newSchedule.cron_expression}
                  onChange={(e) => {
                    setNewSchedule({ ...newSchedule, cron_expression: e.target.value });
                    setCronFields(parseCronExpression(e.target.value));
                    setCronExplanation(explainCronExpression(e.target.value));
                  }}
                  required
                  placeholder={t('schedules.cron_placeholder')}
                />
                {cronExplanation && (
                  <div className="cron-explanation">
                    <strong>{t('schedules.cron_explanation')}</strong> {cronExplanation}
                  </div>
                )}
                <div className="form-help">{t('schedules.cron_help')}</div>
              </div>
              <div className="form-group">
                <label htmlFor="enabled">{t('schedules.enabled')}</label>
                <select
                  id="enabled"
                  value={newSchedule.active ? 'true' : 'false'}
                  onChange={(e) => setNewSchedule({ ...newSchedule, active: e.target.value === 'true' })}
                >
                  <option value="true">{t('domains.enabled')}</option>
                  <option value="false">{t('domains.disabled')}</option>
                </select>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedDomains([]);
                    setTaskType('block');
                  }}
                >
                  {t('schedules.cancel')}
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={isLoading || selectedDomains.length === 0}
                >
                  {isLoading ? t('schedules.adding') : t('schedules.add')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 编辑调度任务模态框 */}
      {showEditModal && currentSchedule && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{t('schedules.edit')}</h3>
              <button 
                className="close-btn"
                onClick={handleCloseEditModal}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleUpdateSchedule} className="modal-body">
              <div className="form-group">
                <label htmlFor="edit-name">{t('schedules.name')} <span className="required">*</span></label>
                <input
                  type="text"
                  id="edit-name"
                  value={newSchedule.name}
                  onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
                  required
                  placeholder={t('schedules.name_placeholder')}
                />
              </div>
              <div className="form-group">
                <label htmlFor="edit-description">{t('schedules.description')}</label>
                <textarea
                  id="edit-description"
                  value={newSchedule.description || ''}
                  onChange={(e) => setNewSchedule({ ...newSchedule, description: e.target.value })}
                  placeholder={t('schedules.description_placeholder')}
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label htmlFor="edit-cron_expression">{t('schedules.cron_expression')} <span className="required">*</span></label>
                <input
                  type="text"
                  id="edit-cron_expression"
                  value={newSchedule.cron_expression}
                  onChange={(e) => setNewSchedule({ ...newSchedule, cron_expression: e.target.value })}
                  required
                  placeholder={t('schedules.cron_placeholder')}
                />
                <div className="form-help">{t('schedules.cron_help')}</div>
              </div>
              <div className="form-group">
                <label htmlFor="edit-enabled">{t('schedules.enabled')}</label>
                <select
                  id="edit-enabled"
                  value={newSchedule.active ? 'true' : 'false'}
                  onChange={(e) => setNewSchedule({ ...newSchedule, active: e.target.value === 'true' })}
                >
                  <option value="true">{t('domains.enabled')}</option>
                  <option value="false">{t('domains.disabled')}</option>
                </select>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={handleCloseEditModal}
                >
                  {t('schedules.cancel')}
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? t('schedules.updating') : t('schedules.edit')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleManager;
