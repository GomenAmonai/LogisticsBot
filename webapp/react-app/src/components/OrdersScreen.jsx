import React, { useState, useEffect } from 'react'
import './OrdersScreen.css'
import { getOrders } from '../services/api'
import OrderCard from './OrderCard'

const OrdersScreen = ({ user }) => {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="orders-screen">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="orders-screen">
      <div className="orders-header">
        <h1>Мои заказы</h1>
        <p className="orders-subtitle">Все ваши заказы в одном месте</p>
      </div>

      <div className="orders-content">
        {orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📦</div>
            <h2>У вас пока нет заказов</h2>
            <p>Создайте первый заказ через меню</p>
          </div>
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

export default OrdersScreen

