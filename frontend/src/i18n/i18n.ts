import zhTranslations from './zh.json';
import enTranslations from './en.json';

// 定义支持的语言类型
export type Language = 'zh' | 'en';

// 定义翻译键类型
export type TranslationKey = keyof typeof zhTranslations;

// 简化翻译键路径类型，避免过深递归
export type TranslationKeyPaths = string;

// 合并翻译类型
type Translations = typeof zhTranslations;

// 翻译管理类
export class I18nManager {
  private static instance: I18nManager;
  private currentLanguage: Language;
  private translations: Record<Language, Translations>;

  private constructor() {
    // 从localStorage获取保存的语言设置，默认使用英文
    const savedLanguage = localStorage.getItem('language') as Language | null;
    this.currentLanguage = savedLanguage || 'en';

    // 初始化翻译数据
    this.translations = {
      zh: zhTranslations,
      en: enTranslations
    };

    // 监听语言变化事件
    window.addEventListener('languagechange', () => {
      this.loadLanguage(this.currentLanguage);
    });
  }

  // 单例模式获取实例
  public static getInstance(): I18nManager {
    if (!I18nManager.instance) {
      I18nManager.instance = new I18nManager();
    }
    return I18nManager.instance;
  }

  // 设置当前语言
  public setLanguage(language: Language): void {
    this.currentLanguage = language;
    localStorage.setItem('language', language);
    this.loadLanguage(language);
  }

  // 获取当前语言
  public getLanguage(): Language {
    return this.currentLanguage;
  }

  // 加载语言
  private loadLanguage(language: Language): void {
    // 更新HTML根元素的lang属性
    document.documentElement.lang = language;
    
    // 触发自定义事件，通知应用语言已变化
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language } }));
  }

  // 获取翻译
  public t(key: TranslationKeyPaths): string {
    const keys = key.split('.');
    let value: any = this.translations[this.currentLanguage];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // 如果找不到对应的翻译，返回原键
        return key;
      }
    }

    return typeof value === 'string' ? value : key;
  }

  // 切换语言
  public toggleLanguage(): void {
    const newLanguage = this.currentLanguage === 'zh' ? 'en' : 'zh';
    this.setLanguage(newLanguage);
  }
}

// 创建全局实例
export const i18n = I18nManager.getInstance();

// 导出翻译函数
export const t = (key: TranslationKeyPaths): string => i18n.t(key);

// 导出语言切换函数
export const setLanguage = (language: Language): void => i18n.setLanguage(language);

export const getLanguage = (): Language => i18n.getLanguage();

export const toggleLanguage = (): void => i18n.toggleLanguage();