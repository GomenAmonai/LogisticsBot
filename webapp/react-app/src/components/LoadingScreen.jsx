import React from 'react'
import './LoadingScreen.css'

const LoadingScreen = () => {
  return (
    <div className="loading-screen">
      <div className="loading-content">
        <div className="spinner"></div>
        <h2>Загрузка...</h2>
        <p>Подключение к платформе</p>
      </div>
    </div>
  )
}

export default LoadingScreen

