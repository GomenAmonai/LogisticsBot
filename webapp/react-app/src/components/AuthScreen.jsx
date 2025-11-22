import React from 'react'
import './AuthScreen.css'

const AuthScreen = ({ onAuth }) => {
  return (
    <div className="auth-screen">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo">🚚</div>
          <h1>Платформа доставки</h1>
          <p>Связь между клиентами и логистами</p>
        </div>
        
        <div className="auth-content">
          <p className="auth-description">
            Откройте это приложение через Telegram бота для автоматической авторизации
          </p>
          
          <button 
            className="btn btn-primary btn-large"
            onClick={() => onAuth(true)}
          >
            Войти (тестовый режим)
          </button>
        </div>
      </div>
    </div>
  )
}

export default AuthScreen

