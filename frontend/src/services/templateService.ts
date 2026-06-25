// 模板服务

// 本地存储键名
const TEMPLATES_STORAGE_KEY = 'website_restriction_templates';

// 定义模板类型
export interface Template {
  id: string;
  name: {
    en: string;
    zh: string;
  };
  description: {
    en: string;
    zh: string;
  };
  isBuiltIn: boolean;
  content: any;
  source: string;
  createdAt: string;
  updatedAt: string;
}

// 定义默认模板
export const defaultTemplates: Template[] = [
  {
    id: '1',
    name: {
      en: 'Default Block List',
      zh: '默认阻止列表'
    },
    description: {
      en: 'Default blocked domains template',
      zh: '默认阻止域名模板'
    },
    isBuiltIn: true,
    content: { domains: ['facebook.com', 'twitter.com', 'instagram.com'] },
    source: 'restricted-sites.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '2',
    name: {
      en: 'Social Media Block',
      zh: '社交媒体阻止'
    },
    description: {
      en: 'Block major social media sites',
      zh: '阻止主要社交媒体网站'
    },
    isBuiltIn: true,
    content: { domains: ['facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'linkedin.com'] },
    source: 'socialmedia-blocklist.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '3',
    name: {
      en: 'News Sites Block',
      zh: '新闻网站阻止'
    },
    description: {
      en: 'Block major news websites',
      zh: '阻止主要新闻网站'
    },
    isBuiltIn: true,
    content: { domains: ['cnn.com', 'bbc.com', 'nytimes.com'] },
    source: 'news-blocklist.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '4',
    name: {
      en: 'Video Streaming Block',
      zh: '视频流媒体阻止'
    },
    description: {
      en: 'Block video streaming sites',
      zh: '阻止视频流媒体网站'
    },
    isBuiltIn: true,
    content: { domains: ['youtube.com', 'netflix.com', 'disneyplus.com'] },
    source: 'streaming-block.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '5',
    name: {
      en: 'Gaming Sites Block',
      zh: '游戏网站阻止'
    },
    description: {
      en: 'Block online gaming websites',
      zh: '阻止在线游戏网站'
    },
    isBuiltIn: true,
    content: { domains: ['steamcommunity.com', 'battlenet.com', 'origin.com'] },
    source: 'gaming-block.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '6',
    name: {
      en: 'Productivity Focus',
      zh: '生产力专注'
    },
    description: {
      en: 'Block distracting websites to improve productivity',
      zh: '阻止分散注意力的网站，提高生产力'
    },
    isBuiltIn: true,
    content: { domains: ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com'] },
    source: 'productivity-zone.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '7',
    name: {
      en: 'Education Only',
      zh: '仅教育用途'
    },
    description: {
      en: 'Allow only educational websites',
      zh: '仅允许教育网站'
    },
    isBuiltIn: true,
    content: { 
      allowedDomains: ['khanacademy.org', 'coursera.org', 'edX.org'],
      blockAllOthers: true 
    },
    source: 'edu-safe.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '8',
    name: {
      en: 'Development Tools',
      zh: '开发工具'
    },
    description: {
      en: 'Block non-development websites during work hours',
      zh: '工作时间阻止非开发网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'netflix.com'],
      allowedDomains: ['github.com', 'stackoverflow.com', 'mdn.io', 'npmjs.com']
    },
    source: 'dev-tools.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '9',
    name: {
      en: 'Parental Control',
      zh: '家长控制'
    },
    description: {
      en: 'Block inappropriate websites for children',
      zh: '阻止儿童不宜的网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['adult-content.example.com', 'gambling.example.com', 'violence.example.com'],
      allowedDomains: ['disney.com', 'nickjr.com', 'pbs.org']
    },
    source: 'safe-kids.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '10',
    name: {
      en: 'Enterprise Security',
      zh: '企业安全'
    },
    description: {
      en: 'Block high-risk security websites',
      zh: '阻止高风险安全网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['malware.example.com', 'phishing.example.com', 'spyware.example.com'],
      categories: ['malware', 'phishing', 'spyware']
    },
    source: 'enterprise-security.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '11',
    name: {
      en: 'News and Media',
      zh: '新闻和媒体'
    },
    description: {
      en: 'Block news and media websites',
      zh: '阻止新闻和媒体网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['cnn.com', 'bbc.com', 'nytimes.com', 'foxnews.com', 'msnbc.com']
    },
    source: 'media-blocklist.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '12',
    name: {
      en: 'Streaming Services',
      zh: '流媒体服务'
    },
    description: {
      en: 'Block all streaming services',
      zh: '阻止所有流媒体服务'
    },
    isBuiltIn: true,
    content: { 
      domains: ['youtube.com', 'netflix.com', 'disneyplus.com', 'hulu.com', 'amazonprime.com']
    },
    source: 'streaming-restrict.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '13',
    name: {
      en: 'Social Media Lite',
      zh: '社交媒体精简版'
    },
    description: {
      en: 'Block only the most distracting social media sites',
      zh: '仅阻止最分散注意力的社交媒体网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['facebook.com', 'instagram.com', 'tiktok.com']
    },
    source: 'social-lite-block.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '14',
    name: {
      en: 'Shopping Websites',
      zh: '购物网站'
    },
    description: {
      en: 'Block online shopping websites',
      zh: '阻止在线购物网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['amazon.com', 'ebay.com', 'alibaba.com', 'taobao.com', 'jd.com']
    },
    source: 'shopping-blocklist.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '15',
    name: {
      en: 'Cryptocurrency Sites',
      zh: '加密货币网站'
    },
    description: {
      en: 'Block cryptocurrency trading and news websites',
      zh: '阻止加密货币交易和新闻网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['coinbase.com', 'binance.com', 'coinmarketcap.com', 'cryptocompare.com']
    },
    source: 'crypto-restrict.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '16',
    name: {
      en: 'Health and Fitness',
      zh: '健康与健身'
    },
    description: {
      en: 'Allow only health and fitness websites',
      zh: '仅允许健康和健身网站'
    },
    isBuiltIn: true,
    content: { 
      allowedDomains: ['webmd.com', 'mayoclinic.org', 'fitbit.com', 'strava.com'],
      blockAllOthers: false
    },
    source: 'health-sites.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '17',
    name: {
      en: 'Finance and Banking',
      zh: '金融和银行'
    },
    description: {
      en: 'Block all non-financial websites',
      zh: '阻止所有非金融网站'
    },
    isBuiltIn: true,
    content: { 
      allowedDomains: ['bankofamerica.com', 'chase.com', 'wellsfargo.com', 'paypal.com'],
      blockAllOthers: true
    },
    source: 'finance-safe.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '18',
    name: {
      en: 'Travel Websites',
      zh: '旅游网站'
    },
    description: {
      en: 'Block travel-related websites',
      zh: '阻止旅游相关网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['expedia.com', 'booking.com', 'airbnb.com', 'kayak.com', 'orbitz.com']
    },
    source: 'travel-blocklist.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '19',
    name: {
      en: 'Food and Recipe',
      zh: '美食和食谱'
    },
    description: {
      en: 'Allow only food and recipe websites',
      zh: '仅允许美食和食谱网站'
    },
    isBuiltIn: true,
    content: { 
      allowedDomains: ['allrecipes.com', 'foodnetwork.com', 'epicurious.com', 'bonappetit.com'],
      blockAllOthers: false
    },
    source: 'food-sites.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '20',
    name: {
      en: 'Tech News',
      zh: '科技新闻'
    },
    description: {
      en: 'Block technology news websites',
      zh: '阻止科技新闻网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['techcrunch.com', 'wired.com', 'engadget.com', 'theverge.com', 'cnet.com']
    },
    source: 'tech-news-block.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '21',
    name: {
      en: 'Sports Websites',
      zh: '体育网站'
    },
    description: {
      en: 'Block sports-related websites',
      zh: '阻止体育相关网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['espn.com', 'sportsillustrated.com', 'nba.com', 'nfl.com', 'mlb.com']
    },
    source: 'sports-blocklist.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '22',
    name: {
      en: 'Entertainment Sites',
      zh: '娱乐网站'
    },
    description: {
      en: 'Block entertainment and streaming websites',
      zh: '阻止娱乐和流媒体网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['netflix.com', 'disneyplus.com', 'hulu.com', 'amazonprime.com', 'spotify.com']
    },
    source: 'entertainment-block.org',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '23',
    name: {
      en: 'E-commerce Sites',
      zh: '电子商务网站'
    },
    description: {
      en: 'Block online shopping and e-commerce websites',
      zh: '阻止在线购物和电子商务网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['amazon.com', 'ebay.com', 'alibaba.com', 'taobao.com', 'shopify.com']
    },
    source: 'ecommerce-blocklist.com',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '24',
    name: {
      en: 'Gaming Platforms',
      zh: '游戏平台'
    },
    description: {
      en: 'Block gaming platforms and related websites',
      zh: '阻止游戏平台和相关网站'
    },
    isBuiltIn: true,
    content: { 
      domains: ['steamcommunity.com', 'epicgames.com', 'riotgames.com', 'blizzard.com', 'mojang.com']
    },
    source: 'gaming-platforms-block.net',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

// 本地存储辅助函数
export const saveTemplatesToLocalStorage = (templates: Template[]) => {
  localStorage.setItem(TEMPLATES_STORAGE_KEY, JSON.stringify(templates));
};

export const loadTemplatesFromLocalStorage = (): Template[] => {
  const storedTemplates = localStorage.getItem(TEMPLATES_STORAGE_KEY);
  if (storedTemplates) {
    try {
      return JSON.parse(storedTemplates);
    } catch (error) {
      console.error('Failed to parse stored templates:', error);
      return defaultTemplates;
    }
  }
  return defaultTemplates;
};

// 获取默认模板
export const getDefaultTemplateById = (id: string): Template | undefined => {
  return defaultTemplates.find(template => template.id === id);
};

// 模板验证结果类型
export interface TemplateValidationResult {
  valid: boolean;
  error?: string;
  details?: any;
}

// 模板验证函数
export const validateTemplateContent = (content: string): TemplateValidationResult => {
  // 检查JSON语法
  try {
    const parsedContent = JSON.parse(content);
    
    // 检查模板内容结构
    if (typeof parsedContent !== 'object' || parsedContent === null) {
      return {
        valid: false,
        error: 'Template content must be a valid JSON object'
      };
    }
    
    // 检查是否包含有效的模板字段
    const hasValidFields = Object.keys(parsedContent).some(key => 
      ['domains', 'allowedDomains', 'categories', 'blockAllOthers'].includes(key)
    );
    
    if (!hasValidFields) {
      return {
        valid: false,
        error: 'Template content must contain at least one valid field: domains, allowedDomains, categories, or blockAllOthers'
      };
    }
    
    // 检查domains字段格式
    if (parsedContent.domains && !Array.isArray(parsedContent.domains)) {
      return {
        valid: false,
        error: 'The domains field must be an array'
      };
    }
    
    // 检查allowedDomains字段格式
    if (parsedContent.allowedDomains && !Array.isArray(parsedContent.allowedDomains)) {
      return {
        valid: false,
        error: 'The allowedDomains field must be an array'
      };
    }
    
    // 检查categories字段格式
    if (parsedContent.categories && !Array.isArray(parsedContent.categories)) {
      return {
        valid: false,
        error: 'The categories field must be an array'
      };
    }
    
    // 检查blockAllOthers字段格式
    if (parsedContent.blockAllOthers && typeof parsedContent.blockAllOthers !== 'boolean') {
      return {
        valid: false,
        error: 'The blockAllOthers field must be a boolean value'
      };
    }
    
    return {
      valid: true
    };
  } catch (error) {
    if (error instanceof SyntaxError) {
      return {
        valid: false,
        error: `Invalid JSON syntax: ${error.message}`
      };
    }
    return {
      valid: false,
      error: `Failed to validate template content: ${error instanceof Error ? error.message : String(error)}`
    };
  }
};

// 模板内容格式化
export const formatTemplateContent = (content: any, indent: number = 2): string => {
  try {
    return JSON.stringify(content, null, indent);
  } catch (error) {
    console.error('Failed to format template content:', error);
    return JSON.stringify(content);
  }
};

// 模板内容解析
export const parseTemplateContent = (content: string): any => {
  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('Failed to parse template content:', error);
    return {};
  }
};

// 获取模板的本地化名称
export const getTemplateLocalizedName = (template: Template, language: 'en' | 'zh' = 'en'): string => {
  return template.name[language] || template.name.en;
};

// 获取模板的本地化描述
export const getTemplateLocalizedDescription = (template: Template, language: 'en' | 'zh' = 'en'): string => {
  return template.description[language] || template.description.en;
};

// 模板服务类
export class TemplateService {
  private static instance: TemplateService;
  private templates: Template[] = [];
  private cache: Map<string, any> = new Map();

  private constructor() {
    this.loadTemplates();
  }

  // 单例模式
  public static getInstance(): TemplateService {
    if (!TemplateService.instance) {
      TemplateService.instance = new TemplateService();
    }
    return TemplateService.instance;
  }

  // 加载模板
  public loadTemplates(): Template[] {
    this.templates = loadTemplatesFromLocalStorage();
    this.cache.clear(); // 清除缓存
    return this.templates;
  }

  // 获取所有模板
  public getTemplates(): Template[] {
    return this.templates;
  }

  // 获取模板
  public getTemplateById(id: string): Template | undefined {
    return this.templates.find(template => template.id === id);
  }

  // 添加模板
  public addTemplate(template: Omit<Template, 'id' | 'createdAt' | 'updatedAt'>): Template {
    const newTemplate: Template = {
      ...template,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    this.templates = [...this.templates, newTemplate];
    saveTemplatesToLocalStorage(this.templates);
    return newTemplate;
  }

  // 更新模板
  public updateTemplate(id: string, updates: Partial<Template>): Template | undefined {
    const templateIndex = this.templates.findIndex(template => template.id === id);
    if (templateIndex === -1) {
      return undefined;
    }
    
    const updatedTemplate: Template = {
      ...this.templates[templateIndex],
      ...updates,
      updatedAt: new Date().toISOString()
    };
    
    this.templates[templateIndex] = updatedTemplate;
    saveTemplatesToLocalStorage(this.templates);
    this.cache.delete(id); // 清除缓存
    return updatedTemplate;
  }

  // 删除模板
  public deleteTemplate(id: string): boolean {
    const template = this.templates.find(t => t.id === id);
    if (!template || template.isBuiltIn) {
      return false;
    }
    
    this.templates = this.templates.filter(template => template.id !== id);
    saveTemplatesToLocalStorage(this.templates);
    this.cache.delete(id); // 清除缓存
    return true;
  }

  // 批量删除模板
  public batchDeleteTemplates(ids: string[]): number {
    const builtInTemplateIds = this.templates
      .filter(template => template.isBuiltIn)
      .map(template => template.id);
    
    const deletableIds = ids.filter(id => !builtInTemplateIds.includes(id));
    this.templates = this.templates.filter(template => !deletableIds.includes(template.id));
    saveTemplatesToLocalStorage(this.templates);
    
    // 清除缓存
    deletableIds.forEach(id => this.cache.delete(id));
    
    return deletableIds.length;
  }

  // 恢复默认模板
  public restoreDefaultTemplates(): Template[] {
    this.templates = [...defaultTemplates];
    saveTemplatesToLocalStorage(this.templates);
    this.cache.clear(); // 清除缓存
    return this.templates;
  }

  // 恢复单个模板到默认状态
  public restoreTemplateToDefault(id: string): Template | undefined {
    const defaultTemplate = getDefaultTemplateById(id);
    if (!defaultTemplate) {
      return undefined;
    }
    
    const templateIndex = this.templates.findIndex(template => template.id === id);
    if (templateIndex === -1) {
      return undefined;
    }
    
    const updatedTemplate: Template = {
      ...defaultTemplate,
      createdAt: this.templates[templateIndex].createdAt, // 保留原创建时间
      updatedAt: new Date().toISOString()
    };
    
    this.templates[templateIndex] = updatedTemplate;
    saveTemplatesToLocalStorage(this.templates);
    this.cache.delete(id); // 清除缓存
    return updatedTemplate;
  }

  // 获取模板内容（带缓存）
  public getTemplateContent(id: string): any {
    if (this.cache.has(id)) {
      return this.cache.get(id);
    }
    
    const template = this.getTemplateById(id);
    if (template) {
      this.cache.set(id, template.content);
      return template.content;
    }
    
    return null;
  }

  // 验证模板内容
  public validateTemplate(templateContent: string): TemplateValidationResult {
    return validateTemplateContent(templateContent);
  }

  // 格式化模板内容
  public formatContent(content: any): string {
    return formatTemplateContent(content);
  }

  // 解析模板内容
  public parseContent(content: string): any {
    return parseTemplateContent(content);
  }

  // 应用模板
  public applyTemplate(templateId: string): boolean {
    try {
      const template = this.getTemplateById(templateId);
      if (!template) {
        throw new Error('Template not found');
      }

      // 这里可以添加模板应用的实际逻辑
      // 例如：保存到本地存储、发送到服务器、应用到当前配置等
      
      // 模拟模板应用成功
      console.log('Applying template:', template.name.en, template.content);
      
      // 可以将模板内容保存到特定的存储键中，供其他组件使用
      localStorage.setItem('applied_template', JSON.stringify({
        templateId: template.id,
        name: template.name,
        content: template.content,
        appliedAt: new Date().toISOString()
      }));
      
      return true;
    } catch (error) {
      console.error('Failed to apply template:', error);
      return false;
    }
  }
}

// 导出默认实例
export const templateService = TemplateService.getInstance();
