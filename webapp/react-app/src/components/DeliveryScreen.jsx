import React, { useState, useEffect } from 'react'
import './DeliveryScreen.css'
import { getOrders, getOrderTracking, contactLogist } from '../services/api'
import OrderCard from './OrderCard'

const DeliveryScreen = ({ user }) => {
  const [orders, setOrders] = useState([])
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [tracking, setTracking] = useState(null)
  const [loading, setLoading] = useState(true)
  const [contacting, setContacting] = useState(false)

  useEffect(() => {
    loadOrders()
  }, [])

  useEffect(() => {
    if (selectedOrder) {
      loadTracking(selectedOrder.id)
    }
  }, [selectedOrder])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const data = await getOrders()
      // Показываем только заказы в процессе доставки
      const activeOrders = (data.orders || []).filter(
        order => order.status !== 'completed' && order.status !== 'cancelled'
      )
      setOrders(activeOrders)
    } catch (error) {
      console.error('Ошибка загрузки заказов:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTracking = async (orderId) => {
    try {
      const data = await getOrderTracking(orderId)
      setTracking(data.tracking || [])
    } catch (error) {
      console.error('Ошибка загрузки отслеживания:', error)
    }
  }

  const handleContactLogist = async (orderId) => {
    try {
      setContacting(true)
      const result = await contactLogist(orderId)
      
      if (window.Telegram?.WebApp) {
        if (result.success) {
          window.Telegram.WebApp.showAlert('Тикет создан! Менеджер свяжется с вами в ближайшее время.')
        } else {
          window.Telegram.WebApp.showAlert('Ошибка создания тикета. Попробуйте позже.')
        }
      }
    } catch (error) {
      console.error('Ошибка связи с логистом:', error)
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Ошибка связи с менеджером')
      }
    } finally {
      setContacting(false)
    }
  }

  const getStatusInfo = (status) => {
    const statuses = {
      'pending': { text: 'Ожидает обработки', emoji: '⏳', color: '#fbbf24' },
      'in_progress': { text: 'В пути', emoji: '🚚', color: '#60a5fa' },
      'out_for_delivery': { text: 'Доставляется', emoji: '📦', color: '#34d399' },
      'delivered': { text: 'Доставлен', emoji: '✅', color: '#10b981' }
    }
    return statuses[status] || { text: status, emoji: '❓', color: '#6b7280' }
  }

  if (loading) {
    return (
      <div className="delivery-screen">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  if (selectedOrder) {
    const statusInfo = getStatusInfo(selectedOrder.status)
    
    return (
      <div className="delivery-screen">
        <div className="delivery-header">
          <button
            className="back-button"
            onClick={() => setSelectedOrder(null)}
          >
            ← Назад
          </button>
          <h2>Отслеживание заказа #{selectedOrder.id}</h2>
        </div>

        <div className="delivery-content">
          <div className="order-details-card">
            <div className="order-status-badge" style={{ backgroundColor: statusInfo.color + '20', color: statusInfo.color }}>
              <span className="status-emoji">{statusInfo.emoji}</span>
              <span className="status-text">{statusInfo.text}</span>
            </div>

            <div className="order-info">
              <div className="info-row">
                <span className="info-label">Откуда:</span>
                <span className="info-value">{selectedOrder.from_address || 'Не указано'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Куда:</span>
                <span className="info-value">{selectedOrder.to_address || 'Не указано'}</span>
              </div>
              {selectedOrder.tracking_number && (
                <div className="info-row">
                  <span className="info-label">Трек-номер:</span>
                  <span className="info-value tracking-number">{selectedOrder.tracking_number}</span>
                </div>
              )}
            </div>
          </div>

          {/* Карта (заглушка - можно интегрировать Yandex Maps или Google Maps) */}
          <div className="map-container">
            <div className="map-placeholder">
              <div className="map-icon">🗺️</div>
              <p>Карта отслеживания</p>
              <p className="map-note">Текущее местоположение: {selectedOrder.from_address || 'Загрузка...'}</p>
            </div>
          </div>

          {/* История отслеживания */}
          {tracking && tracking.length > 0 && (
            <div className="tracking-history">
              <h3>История перемещений</h3>
              <div className="timeline">
                {tracking.map((item, index) => (
                  <div key={index} className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                      <div className="timeline-status">{item.status}</div>
                      <div className="timeline-location">{item.location}</div>
                      <div className="timeline-description">{item.description}</div>
                      <div className="timeline-date">
                        {new Date(item.created_at).toLocaleString('ru-RU')}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Информация о логисте */}
          {selectedOrder.manager_id && (
            <div className="logist-info-card">
              <h3>📦 Кто обрабатывает заказ</h3>
              <p className="logist-name">Менеджер назначен</p>
              <button
                className="btn btn-primary contact-logist-btn"
                onClick={() => handleContactLogist(selectedOrder.id)}
                disabled={contacting}
              >
                {contacting ? 'Создание тикета...' : '💬 Связаться с менеджером'}
              </button>
              <p className="contact-note">
                Нажмите кнопку, чтобы создать тикет. Менеджер получит уведомление и свяжется с вами.
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="delivery-screen">
      <div className="delivery-header">
        <h2>Доставка</h2>
      </div>

      <div className="delivery-content">
        {orders.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🚚</div>
            <h3>Нет активных доставок</h3>
            <p>У вас пока нет заказов в процессе доставки</p>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map(order => (
              <div
                key={order.id}
                className="order-item"
                onClick={() => setSelectedOrder(order)}
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

export default DeliveryScreen

