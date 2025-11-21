import React, { useState, useEffect } from 'react'
import './AdminView.css'
import { getOrders, getStats } from '../services/api'
import OrderCard from './OrderCard'

const AdminView = ({ user, onLogout }) => {
  const [orders, setOrders] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [ordersData, statsData] = await Promise.all([
        getOrders(),
        getStats()
      ])
      setOrders(ordersData.orders || [])
      setStats(statsData.stats || {})
    } catch (error) {
      console.error('Ошибка загрузки данных:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-view">
      <nav className="navbar">
        <div className="nav-brand">🚚 Логистика</div>
        <div className="nav-user">👑 {user.name}</div>
        <button className="btn btn-small btn-secondary" onClick={onLogout}>
          Выход
        </button>
      </nav>

      <div className="container">
        <h1 className="page-title">Панель администратора</h1>
        
        <div className="stats-grid">
          {Object.entries(stats).map(([key, value]) => (
            <div key={key} className="stat-card card">
              <div className="stat-value">{value}</div>
              <div className="stat-label">{key}</div>
            </div>
          ))}
        </div>

        <h2 className="section-title">Все заказы</h2>
        
        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : (
          <div className="orders-grid">
            {orders.map(order => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminView

