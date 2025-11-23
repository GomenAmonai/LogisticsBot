import React, { useState, useEffect } from 'react'
import './ManagerView.css'
import { getOrders, assignOrder } from '../services/api'
import OrderCard from './OrderCard'
import ChatScreen from './ChatScreen'
import OfferEditor from './OfferEditor'
import UserInfoBar from './UserInfoBar'

const ManagerView = ({ user, onLogout }) => {
  const [activeSection, setActiveSection] = useState('incoming')
  const [incomingOrders, setIncomingOrders] = useState([])
  const [myOrders, setMyOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState(null)
  const [chatOrder, setChatOrder] = useState(null)
  const [offerOrder, setOfferOrder] = useState(null)

  useEffect(() => {
    loadIncoming()
    loadMyOrders()
  }, [])

  useEffect(() => {
    if (activeSection === 'incoming') {
      loadIncoming()
    } else if (activeSection === 'my') {
      loadMyOrders()
    }
  }, [activeSection])

  const loadIncoming = async () => {
    try {
      setLoading(true)
      const data = await getOrders('incoming')
      setIncomingOrders(data.orders || [])
    } catch (error) {
      console.error('Ошибка загрузки входящих заказов:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadMyOrders = async () => {
    try {
      setLoading(true)
      const data = await getOrders('assigned')
      setMyOrders(data.orders || [])
    } catch (error) {
      console.error('Ошибка загрузки заказов менеджера:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = async (orderId) => {
    try {
      setActionLoading(orderId)
      await assignOrder(orderId)
      await Promise.all([loadIncoming(), loadMyOrders()])
      setActiveSection('my')
    } catch (error) {
      console.error('Ошибка назначения заказа:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const renderIncoming = () => {
    if (loading && incomingOrders.length === 0) {
      return <div className="loading">Загрузка...</div>
    }
    if (incomingOrders.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>Нет входящих заказов</h2>
          <p>Новые заявки клиентов появятся здесь</p>
        </div>
      )
    }
    return (
      <div className="orders-grid">
        {incomingOrders.map((order) => (
          <div className="manager-card" key={order.id}>
            <OrderCard order={order} />
            <div className="manager-card-actions">
              <button
                className="btn btn-primary"
                onClick={() => handleAssign(order.id)}
                disabled={actionLoading === order.id}
              >
                {actionLoading === order.id ? 'Назначение...' : 'Взять в работу'}
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderMyOrders = () => {
    if (loading && myOrders.length === 0) {
      return <div className="loading">Загрузка...</div>
    }
    if (myOrders.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h2>У вас пока нет заказов</h2>
          <p>Возьмите заказ из входящих и доведите его до конца</p>
        </div>
      )
    }
    return (
      <div className="orders-grid">
        {myOrders.map((order) => (
          <div className="manager-card" key={order.id}>
            <OrderCard order={order} />
            <div className="manager-card-actions">
              <button className="btn btn-secondary" onClick={() => {
                setChatOrder(order)
                setActiveSection('chat')
              }}>
                💬 Чат
              </button>
              <button className="btn btn-primary" onClick={() => {
                setOfferOrder(order)
                setActiveSection('offer')
              }}>
                📄 Оферта
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const renderChat = () => {
    if (!chatOrder) {
      return (
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h2>Выберите заказ</h2>
          <p>Откройте раздел «Мои заказы» и нажмите «Чат»</p>
        </div>
      )
    }
    return (
      <ChatScreen
        order={chatOrder}
        user={user}
        onBack={() => {
          setChatOrder(null)
          setActiveSection('my')
        }}
      />
    )
  }

  const renderOffer = () => {
    if (!offerOrder) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <h2>Выберите заказ</h2>
          <p>Откройте раздел «Мои заказы» и нажмите «Оферта»</p>
        </div>
      )
    }
    return (
      <OfferEditor
        order={offerOrder}
        onBack={() => {
          setOfferOrder(null)
          setActiveSection('my')
        }}
        onSuccess={async () => {
          setOfferOrder(null)
          await loadMyOrders()
          setActiveSection('my')
        }}
      />
    )
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
        <UserInfoBar user={user} onLogout={onLogout} />
        <h1 className="page-title">Панель логиста</h1>

        <div className="tabs manager-tabs">
          <button
            className={`tab ${activeSection === 'incoming' ? 'active' : ''}`}
            onClick={() => setActiveSection('incoming')}
          >
            Входящие заказы
          </button>
          <button
            className={`tab ${activeSection === 'my' ? 'active' : ''}`}
            onClick={() => setActiveSection('my')}
          >
            Мои заказы
          </button>
          <button
            className={`tab ${activeSection === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveSection('chat')}
          >
            Чат с клиентом
          </button>
          <button
            className={`tab ${activeSection === 'offer' ? 'active' : ''}`}
            onClick={() => setActiveSection('offer')}
          >
            Создание оферты
          </button>
        </div>

        <div className="manager-section">
          {activeSection === 'incoming' && renderIncoming()}
          {activeSection === 'my' && renderMyOrders()}
          {activeSection === 'chat' && renderChat()}
          {activeSection === 'offer' && renderOffer()}
        </div>
      </div>
    </div>
  )
}

export default ManagerView

