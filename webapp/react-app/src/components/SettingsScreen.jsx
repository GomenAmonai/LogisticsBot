import React, { useState, useEffect } from 'react'
import './SettingsScreen.css'
import { useTheme } from '../contexts/ThemeContext'
import { NotificationIcon, MoonIcon, SunIcon, PrivacyIcon, TermsIcon, LogoutIcon } from './Icons'
import PrivacyModal from './PrivacyModal'
import TermsModal from './TermsModal'
import { getCurrentUser, updateUserProfile } from '../services/api'

const SettingsScreen = ({ user, onLogout }) => {
  const { theme, toggleTheme } = useTheme()
  const [notifications, setNotifications] = useState(false)
  const [showPrivacyModal, setShowPrivacyModal] = useState(false)
  const [showTermsModal, setShowTermsModal] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const userData = await getCurrentUser()
      setNotifications(userData.notifications_enabled || false)
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error)
    }
  }

  const handleNotificationsChange = async (enabled) => {
    const previousValue = notifications
    setNotifications(enabled)
    try {
      setLoading(true)
      await updateUserProfile({ notifications_enabled: enabled })
    } catch (error) {
      console.error('Ошибка обновления уведомлений:', error)
      // Откатываем изменение при ошибке
      setNotifications(previousValue)
      const errorMessage = error.message || 'Не удалось обновить настройки уведомлений'
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(errorMessage)
      } else {
        alert(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="settings-screen">
        <div className="settings-header">
          <h2>Настройки</h2>
        </div>

        <div className="settings-content">
          <div className="settings-section">
            <h3>Уведомления</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <div className="setting-icon">
                  <NotificationIcon size={20} />
                </div>
                <div>
                  <span className="setting-label">Push-уведомления</span>
                  <span className="setting-description">Получать уведомления о статусе заказов</span>
                </div>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={notifications}
                  onChange={(e) => handleNotificationsChange(e.target.checked)}
                  disabled={loading}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-section">
            <h3>Внешний вид</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <div className="setting-icon">
                  {theme === 'dark' ? <MoonIcon size={20} /> : <SunIcon size={20} />}
                </div>
                <div>
                  <span className="setting-label">Темная тема</span>
                  <span className="setting-description">Использовать темную тему интерфейса</span>
                </div>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={theme === 'dark'}
                  onChange={toggleTheme}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-section">
            <h3>О приложении</h3>
            
            <div className="setting-item">
              <span className="setting-label">Версия</span>
              <span className="setting-value">1.0.0</span>
            </div>
            
            <div className="setting-item">
              <span className="setting-label">Поддержка</span>
              <span className="setting-value">support@logistics.com</span>
            </div>
            
            <div className="setting-item clickable" onClick={() => setShowPrivacyModal(true)}>
              <div className="setting-info">
                <div className="setting-icon">
                  <PrivacyIcon size={20} />
                </div>
                <span className="setting-label">Политика конфиденциальности</span>
              </div>
              <span className="setting-value">→</span>
            </div>
            
            <div className="setting-item clickable" onClick={() => setShowTermsModal(true)}>
              <div className="setting-info">
                <div className="setting-icon">
                  <TermsIcon size={20} />
                </div>
                <span className="setting-label">Условия использования</span>
              </div>
              <span className="setting-value">→</span>
            </div>
          </div>

          <div className="settings-section">
            <button className="btn btn-danger" onClick={onLogout}>
              <LogoutIcon size={18} />
              Выйти из аккаунта
            </button>
          </div>
        </div>
      </div>

      {showPrivacyModal && <PrivacyModal onClose={() => setShowPrivacyModal(false)} />}
      {showTermsModal && <TermsModal onClose={() => setShowTermsModal(false)} />}
    </>
  )
}

export default SettingsScreen

