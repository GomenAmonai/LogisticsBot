import React from 'react'
import './OrderCard.css'

const OrderCard = ({ order }) => {
  const getStatusText = (status) => {
    const statuses = {
      'pending': 'Ожидает',
      'accepted': 'Принят',
      'in_transit': 'В пути',
      'delivered': 'Доставлен',
      'cancelled': 'Отменен'
    }
    return statuses[status] || status
  }

  return (
    <div className="order-card card fade-in">
      <div className="order-header">
        <div className="order-id">Заказ #{order.id}</div>
        <span className={`status-badge status-${order.status}`}>
          {getStatusText(order.status)}
        </span>
      </div>
      
      <div className="order-body">
        <p className="order-description">
          {order.description || 'Нет описания'}
        </p>
        
        {order.tracking_number && (
          <div className="order-tracking">
            <span className="order-label">Отслеживание:</span>
            <span className="order-value">{order.tracking_number}</span>
          </div>
        )}
        
        {order.from_address && (
          <div className="order-address">
            <span className="order-label">От:</span>
            <span className="order-value">{order.from_address}</span>
          </div>
        )}
        
        {order.to_address && (
          <div className="order-address">
            <span className="order-label">Куда:</span>
            <span className="order-value">{order.to_address}</span>
          </div>
        )}
        
        {order.price && (
          <div className="order-price">
            <span className="order-label">Цена:</span>
            <span className="order-value price">{order.price} ₽</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrderCard

