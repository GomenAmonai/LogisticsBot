import React, { useState, useEffect } from 'react'
import './ClientView.css'
import { getOrders, createOrder } from '../services/api'
import OrderCard from './OrderCard'
import CreateOrderModal from './CreateOrderModal'

const ClientView = ({ user, onLogout }) => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadOrders()
  }, [])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const data = await getOrders()
      setOrders(data.orders || [])
    } catch (error) {
      console.error('Ошибка загрузки заказов:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOrder = async (orderData) => {
    try {
      await createOrder(orderData)
      await loadOrders()
      setShowCreateModal(false)
      
      // Показываем уведомление через Telegram WebApp
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Заказ успешно создан!')
      }
    } catch (error) {
      console.error('Ошибка создания заказа:', error)
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Ошибка создания заказа')
      }
    }
  }

  return (
    <div className="client-view">
      <nav className="navbar">
        <div className="nav-brand">🚚 Логистика</div>
        <div className="nav-user">👤 {user.name}</div>
        <button className="btn btn-small btn-secondary" onClick={onLogout}>
          Выход
        </button>
      </nav>

      <div className="container">
        <div className="page-header">
          <h1>Мои заказы</h1>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            + Создать заказ
          </button>
        </div>

        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <h2>У вас пока нет заказов</h2>
            <p>Создайте первый заказ, нажав кнопку выше</p>
          </div>
        ) : (
          <div className="orders-grid">
            {orders.map(order => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateOrderModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateOrder}
        />
      )}
    </div>
  )
}

export default ClientView

