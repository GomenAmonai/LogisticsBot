import React, { useState, useEffect } from 'react'
import './OrdersScreen.css'
import { getOrders } from '../services/api'
import OrderCard from './OrderCard'

const OrdersScreen = ({ user, onOrderClick, onCreateOrder }) => {
  const [orders, setOrders] = useState([])
  const [filteredOrders, setFilteredOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    loadOrders()
  }, [])

  useEffect(() => {
    filterOrders()
  }, [orders, searchQuery, statusFilter])

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

  const filterOrders = () => {
    let filtered = [...orders]

    // Фильтр по статусу
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter)
    }

    // Поиск
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(order => 
        order.description?.toLowerCase().includes(query) ||
        order.from_address?.toLowerCase().includes(query) ||
        order.to_address?.toLowerCase().includes(query) ||
        order.tracking_number?.toLowerCase().includes(query) ||
        order.id.toString().includes(query)
      )
    }

    setFilteredOrders(filtered)
  }

  const getStatusCounts = () => {
    const counts = {
      all: orders.length,
      pending: 0,
      accepted: 0,
      in_transit: 0,
      delivered: 0,
      cancelled: 0
    }
    
    orders.forEach(order => {
      if (counts[order.status] !== undefined) {
        counts[order.status]++
      }
    })
    
    return counts
  }

  const statusCounts = getStatusCounts()

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
        <div className="header-top">
          <h1>Мои заказы</h1>
          <div className="header-actions">
            {onCreateOrder && (
              <button
                className="btn-create-order"
                onClick={onCreateOrder}
                title="Создать заказ"
              >
                ➕
              </button>
            )}
            <div className="orders-count">{orders.length} заказов</div>
          </div>
        </div>
        
        {/* Поиск */}
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="🔍 Поиск по описанию, адресу, трек-номеру..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Фильтры по статусу */}
        <div className="status-filters">
          <button
            className={`filter-btn ${statusFilter === 'all' ? 'active' : ''}`}
            onClick={() => setStatusFilter('all')}
          >
            Все ({statusCounts.all})
          </button>
          <button
            className={`filter-btn ${statusFilter === 'pending' ? 'active' : ''}`}
            onClick={() => setStatusFilter('pending')}
          >
            ⏳ Ожидают ({statusCounts.pending})
          </button>
          <button
            className={`filter-btn ${statusFilter === 'accepted' ? 'active' : ''}`}
            onClick={() => setStatusFilter('accepted')}
          >
            ✅ Принят ({statusCounts.accepted})
          </button>
          <button
            className={`filter-btn ${statusFilter === 'in_transit' ? 'active' : ''}`}
            onClick={() => setStatusFilter('in_transit')}
          >
            🚚 В пути ({statusCounts.in_transit})
          </button>
          <button
            className={`filter-btn ${statusFilter === 'delivered' ? 'active' : ''}`}
            onClick={() => setStatusFilter('delivered')}
          >
            📦 Доставлен ({statusCounts.delivered})
          </button>
        </div>
      </div>

      <div className="orders-content">
        {filteredOrders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              {searchQuery || statusFilter !== 'all' ? '🔍' : '📦'}
            </div>
            <h2>
              {searchQuery || statusFilter !== 'all' 
                ? 'Заказы не найдены' 
                : 'У вас пока нет заказов'}
            </h2>
            <p>
              {searchQuery || statusFilter !== 'all'
                ? 'Попробуйте изменить фильтры или поисковый запрос'
                : 'Создайте первый заказ через меню'}
            </p>
          </div>
        ) : (
          <div className="orders-grid">
            {filteredOrders.map(order => (
              <div 
                key={order.id} 
                onClick={() => onOrderClick && onOrderClick(order)}
                style={{ cursor: onOrderClick ? 'pointer' : 'default' }}
              >
                <OrderCard order={order} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default OrdersScreen
