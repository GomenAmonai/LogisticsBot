import React, { useState } from 'react'
import './SettingsScreen.css'

const SettingsScreen = ({ user, onLogout }) => {
  const [notifications, setNotifications] = useState(true)
  const [darkMode, setDarkMode] = useState(true)

  return (
    <div className="settings-screen">
      <div className="settings-header">
        <h2>Настройки</h2>
      </div>

      <div className="settings-content">
        <div className="settings-section">
          <h3>Уведомления</h3>
          
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Push-уведомления</span>
              <span className="setting-description">Получать уведомления о статусе заказов</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div className="settings-section">
          <h3>Внешний вид</h3>
          
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Темная тема</span>
              <span className="setting-description">Использовать темную тему интерфейса</span>
            </div>
            <label className="toggle">
              <input
                type="checkbox"
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
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
        </div>

        <div className="settings-section">
          <button className="btn btn-danger" onClick={onLogout}>
            Выйти из аккаунта
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsScreen

