import React from 'react'
import './TicketCard.css'

const TicketCard = ({ ticket, onAccept }) => {
  return (
    <div className="ticket-card card fade-in">
      <div className="ticket-header">
        <div className="ticket-id">Тикет #{ticket.id}</div>
        <span className="order-id">Заказ #{ticket.order_id}</span>
      </div>
      
      <div className="ticket-body">
        <p className="ticket-description">
          {ticket.description || 'Нет описания'}
        </p>
        
        {ticket.from_address && (
          <div className="ticket-info">
            <span className="ticket-label">От:</span>
            <span className="ticket-value">{ticket.from_address}</span>
          </div>
        )}
        
        {ticket.to_address && (
          <div className="ticket-info">
            <span className="ticket-label">Куда:</span>
            <span className="ticket-value">{ticket.to_address}</span>
          </div>
        )}
      </div>
      
      <div className="ticket-actions">
        <button
          className="btn btn-primary"
          onClick={() => onAccept(ticket.id)}
        >
          Принять
        </button>
      </div>
    </div>
  )
}

export default TicketCard

