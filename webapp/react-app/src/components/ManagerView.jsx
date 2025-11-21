import React, { useState, useEffect } from 'react'
import './ManagerView.css'
import { getTickets, getOrders, acceptTicket } from '../services/api'
import TicketCard from './TicketCard'
import OrderCard from './OrderCard'

const ManagerView = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('tickets')
  const [tickets, setTickets] = useState([])
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (activeTab === 'tickets') {
      loadTickets()
    } else {
      loadOrders()
    }
  }, [activeTab])

  const loadTickets = async () => {
    try {
      setLoading(true)
      const data = await getTickets('new')
      setTickets(data.tickets || [])
    } catch (error) {
      console.error('Ошибка загрузки тикетов:', error)
    } finally {
      setLoading(false)
    }
  }

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

  const handleAcceptTicket = async (ticketId) => {
    try {
      await acceptTicket(ticketId)
      await loadTickets()
      await loadOrders()
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Тикет принят!')
      }
    } catch (error) {
      console.error('Ошибка принятия тикета:', error)
    }
  }

  return (
    <div className="manager-view">
      <nav className="navbar">
        <div className="nav-brand">🚚 Логистика</div>
        <div className="nav-user">👨‍💼 {user.name}</div>
        <button className="btn btn-small btn-secondary" onClick={onLogout}>
          Выход
        </button>
      </nav>

      <div className="container">
        <h1 className="page-title">Тикеты и заказы</h1>
        
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'tickets' ? 'active' : ''}`}
            onClick={() => setActiveTab('tickets')}
          >
            Новые тикеты
          </button>
          <button
            className={`tab ${activeTab === 'orders' ? 'active' : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            Мои заказы
          </button>
        </div>

        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : activeTab === 'tickets' ? (
          tickets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <h2>Новых тикетов нет</h2>
            </div>
          ) : (
            <div className="tickets-grid">
              {tickets.map(ticket => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  onAccept={handleAcceptTicket}
                />
              ))}
            </div>
          )
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

export default ManagerView

