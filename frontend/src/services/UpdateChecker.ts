// UpdateChecker.ts - 自动更新检查服务

interface UpdateCheckResult {
  hasUpdate: boolean;
  latestVersion: string;
  currentVersion: string;
  error?: string;
}

class UpdateChecker {
  private readonly CURRENT_VERSION = '4.4';
  private readonly UPDATE_SOURCES = [
    'https://websiteblocker.vercel.app/version.txt',
    'https://websiteblocker-zh.wangstation.ddns-ip.net/version.txt'
  ];
  private readonly REQUEST_TIMEOUT = 5000; // 5秒超时
  private readonly STORAGE_KEYS = {
    LAST_CHECK: 'update_check.last_check',
    CHECK_INTERVAL: 'update_check.interval',
    SKIP_VERSION: 'update_check.skip_version'
  };

  /**
   * 检查是否有更新
   */
  async checkForUpdates(): Promise<UpdateCheckResult> {
    try {
      // 依次尝试所有更新源
      for (const source of this.UPDATE_SOURCES) {
        try {
          const latestVersion = await this.fetchVersion(source);
          if (latestVersion && this.isValidVersion(latestVersion)) {
            const hasUpdate = this.compareVersions(latestVersion, this.CURRENT_VERSION) > 0;
            return {
              hasUpdate,
              latestVersion,
              currentVersion: this.CURRENT_VERSION
            };
          }
        } catch (error) {
          console.warn(`Failed to fetch version from ${source}:`, error);
          // 继续尝试下一个源
          continue;
        }
      }

      // 所有源都失败
      return {
        hasUpdate: false,
        latestVersion: this.CURRENT_VERSION,
        currentVersion: this.CURRENT_VERSION,
        error: 'Failed to check for updates from all sources'
      };
    } catch (error) {
      console.error('Update check failed:', error);
      return {
        hasUpdate: false,
        latestVersion: this.CURRENT_VERSION,
        currentVersion: this.CURRENT_VERSION,
        error: 'Update check failed'
      };
    }
  }

  /**
   * 从指定源获取版本号
   */
  private async fetchVersion(source: string): Promise<string> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.REQUEST_TIMEOUT);

    try {
      const response = await fetch(source, {
        signal: controller.signal,
        headers: {
          'Cache-Control': 'no-cache'
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const content = await response.text();
      return this.parseVersion(content);
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * 解析版本号
   */
  private parseVersion(content: string): string {
    // 提取纯数字版本号，忽略其他内容
    const match = content.trim().match(/^\d+(?:\.\d+)*$/);
    return match ? match[0] : '';
  }

  /**
   * 验证版本号是否有效
   */
  private isValidVersion(version: string): boolean {
    return version.length > 0 && /^\d+(?:\.\d+)*$/.test(version);
  }

  /**
   * 比较版本号
   * @returns 1: latest > current, 0: latest == current, -1: latest < current
   */
  compareVersions(latest: string, current: string): number {
    const latestParts = latest.split('.').map(Number);
    const currentParts = current.split('.').map(Number);

    const maxLength = Math.max(latestParts.length, currentParts.length);

    for (let i = 0; i < maxLength; i++) {
      const latestPart = latestParts[i] || 0;
      const currentPart = currentParts[i] || 0;

      if (latestPart > currentPart) return 1;
      if (latestPart < currentPart) return -1;
    }

    return 0;
  }

  /**
   * 检查是否需要进行更新检查
   */
  shouldCheckForUpdates(): boolean {
    // 检查是否跳过了当前版本
    const skipVersion = localStorage.getItem(this.STORAGE_KEYS.SKIP_VERSION);
    if (skipVersion) {
      return false;
    }

    // 检查上次检查时间
    const lastCheck = localStorage.getItem(this.STORAGE_KEYS.LAST_CHECK);
    if (!lastCheck) {
      return true; // 第一次使用，需要检查
    }

    // 默认检查间隔：24小时
    const interval = parseInt(localStorage.getItem(this.STORAGE_KEYS.CHECK_INTERVAL) || '86400000');
    const now = Date.now();
    const lastCheckTime = parseInt(lastCheck);

    return now - lastCheckTime >= interval;
  }

  /**
   * 更新最后检查时间
   */
  updateLastCheckTime(): void {
    localStorage.setItem(this.STORAGE_KEYS.LAST_CHECK, Date.now().toString());
  }

  /**
   * 设置跳过的版本
   */
  skipVersion(version: string): void {
    localStorage.setItem(this.STORAGE_KEYS.SKIP_VERSION, version);
  }

  /**
   * 清除跳过的版本
   */
  clearSkipVersion(): void {
    localStorage.removeItem(this.STORAGE_KEYS.SKIP_VERSION);
  }

  /**
   * 获取当前版本
   */
  getCurrentVersion(): string {
    return this.CURRENT_VERSION;
  }

  /**
   * 设置更新检查间隔
   */
  setCheckInterval(intervalMs: number): void {
    localStorage.setItem(this.STORAGE_KEYS.CHECK_INTERVAL, intervalMs.toString());
  }

  /**
   * 手动检查更新
   */
  async manualCheck(): Promise<UpdateCheckResult> {
    const result = await this.checkForUpdates();
    this.updateLastCheckTime();
    return result;
  }
}

// 导出单例实例
const updateChecker = new UpdateChecker();
export default updateChecker;
export type { UpdateCheckResult };