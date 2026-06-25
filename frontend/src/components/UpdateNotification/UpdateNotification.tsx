import React, { useState } from 'react';
import { t } from '../../i18n/i18n';
import './UpdateNotification.css';
import updateChecker from '../../services/UpdateChecker';

interface UpdateNotificationProps {
  latestVersion: string;
  currentVersion: string;
  onClose: () => void;
  onUpdate: () => void;
}

const UpdateNotification: React.FC<UpdateNotificationProps> = ({
  latestVersion,
  currentVersion,
  onClose,
  onUpdate
}) => {
  const [skipVersion, setSkipVersion] = useState(false);

  const handleClose = () => {
    if (skipVersion) {
      updateChecker.skipVersion(latestVersion);
    }
    onClose();
  };

  const handleUpdate = () => {
    onUpdate();
    onClose();
  };

  return (
    <div className="update-notification-overlay">
      <div className="update-notification">
        {/* 头部 */}
        <div className="update-notification-header">
          <h3>{t('update.title')}</h3>
          <button 
            className="update-notification-close" 
            onClick={handleClose}
            aria-label={t('update.close')}
          >
            ×
          </button>
        </div>

        {/* 内容 */}
        <div className="update-notification-content">
          <div className="update-notification-icon">
            <i className="icon-update"></i>
          </div>
          <div className="update-notification-info">
            <p className="update-notification-message">
              {t('update.new_version_available')}
            </p>
            <div className="update-notification-versions">
              <div className="version-item">
                <span className="version-label">{t('update.current_version')}:</span>
                <span className="version-value current">{currentVersion}</span>
              </div>
              <div className="version-item">
                <span className="version-label">{t('update.latest_version')}:</span>
                <span className="version-value latest">{latestVersion}</span>
              </div>
            </div>
            <p className="update-notification-description">
              {t('update.update_description')}
            </p>
          </div>
        </div>

        {/* 选项 */}
        <div className="update-notification-options">
          <label className="update-notification-checkbox">
            <input 
              type="checkbox" 
              checked={skipVersion} 
              onChange={(e) => setSkipVersion(e.target.checked)}
            />
            <span>{t('update.skip_this_version')}</span>
          </label>
        </div>

        {/* 操作按钮 */}
        <div className="update-notification-actions">
          <button 
            className="btn btn-secondary" 
            onClick={handleClose}
          >
            {t('update.later')}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleUpdate}
          >
            {t('update.update_now')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdateNotification;