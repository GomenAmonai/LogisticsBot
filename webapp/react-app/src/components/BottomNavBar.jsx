import React from 'react'
import './BottomNavBar.css'

const BottomNavBar = ({ activeTab, onTabChange }) => {
  return (
    <div className="bottom-nav-bar">
      <button
        className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
        onClick={() => onTabChange('home')}
      >
        <span className="nav-icon">🏠</span>
        <span className="nav-label">Главная</span>
      </button>
      
      <button
        className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
        onClick={() => onTabChange('profile')}
      >
        <span className="nav-icon">👤</span>
        <span className="nav-label">Профиль</span>
      </button>
      
      <button
        className={`nav-item ${activeTab === 'delivery' ? 'active' : ''}`}
        onClick={() => onTabChange('delivery')}
      >
        <span className="nav-icon">🚚</span>
        <span className="nav-label">Доставка</span>
      </button>
      
      <button
        className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
        onClick={() => onTabChange('settings')}
      >
        <span className="nav-icon">⚙️</span>
        <span className="nav-label">Настройки</span>
      </button>
    </div>
  )
}

export default BottomNavBar

