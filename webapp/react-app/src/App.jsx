import React, { useState, useEffect } from 'react'
import './App.css'
import AuthScreen from './components/AuthScreen'
import ClientView from './components/ClientView'
import ManagerView from './components/ManagerView'
import AdminView from './components/AdminView'
import LoadingScreen from './components/LoadingScreen'
import { authUser, getCurrentUser } from './services/api'

function App() {
  const [loading, setLoading] = useState(true)
  const [authenticated, setAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    initApp()
  }, [])

  const initApp = async () => {
    try {
      // Пытаемся авторизоваться через Telegram WebApp
      const tg = window.Telegram?.WebApp
      
      if (tg) {
        tg.ready()
        tg.expand()
        
        const initData = tg.initData
        if (initData) {
          const response = await authUser(initData)
          if (response.success) {
            setUser(response.user)
            setAuthenticated(true)
          }
        }
      }
      
      // Для тестирования без Telegram
      const testUser = localStorage.getItem('testUser')
      if (testUser) {
        setUser(JSON.parse(testUser))
        setAuthenticated(true)
      }
    } catch (error) {
      console.error('Ошибка инициализации:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAuth = async (testMode = false) => {
    if (testMode) {
      // Тестовый режим
      const testUser = { id: 1, name: 'Test User', role: 'client' }
      localStorage.setItem('testUser', JSON.stringify(testUser))
      setUser(testUser)
      setAuthenticated(true)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('testUser')
    setUser(null)
    setAuthenticated(false)
  }

  if (loading) {
    return <LoadingScreen />
  }

  if (!authenticated) {
    return <AuthScreen onAuth={handleAuth} />
  }

  return (
    <div className="app">
      {user?.role === 'client' && <ClientView user={user} onLogout={handleLogout} />}
      {user?.role === 'manager' && <ManagerView user={user} onLogout={handleLogout} />}
      {user?.role === 'admin' && <AdminView user={user} onLogout={handleLogout} />}
    </div>
  )
}

export default App

