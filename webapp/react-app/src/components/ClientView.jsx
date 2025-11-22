import React, { useState } from 'react'
import './ClientView.css'
import BottomNavBar from './BottomNavBar'
import OrdersScreen from './OrdersScreen'
import ProfileScreen from './ProfileScreen'
import DeliveryScreen from './DeliveryScreen'
import SettingsScreen from './SettingsScreen'
import CreateOrderScreen from './CreateOrderScreen'

const ClientView = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('home')
  const [showCreateOrder, setShowCreateOrder] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState(null)

  const handleOrderClick = (order) => {
    setSelectedOrder(order)
    // Можно открыть детали заказа или перейти на экран доставки
    setActiveTab('delivery')
  }

  const [refreshKey, setRefreshKey] = useState(0)

  const handleCreateOrderSuccess = () => {
    setShowCreateOrder(false)
    setActiveTab('home')
    // Обновляем список заказов
    setRefreshKey(prev => prev + 1)
  }

  const renderScreen = () => {
    if (showCreateOrder) {
      return (
        <CreateOrderScreen
          user={user}
          onBack={() => setShowCreateOrder(false)}
          onSuccess={handleCreateOrderSuccess}
        />
      )
    }

    switch (activeTab) {
      case 'home':
        return (
          <OrdersScreen
            key={refreshKey}
            user={user}
            onOrderClick={handleOrderClick}
            onCreateOrder={() => setShowCreateOrder(true)}
          />
        )
      case 'profile':
        return <ProfileScreen user={user} />
      case 'orders':
        return (
          <OrdersScreen
            key={refreshKey}
            user={user}
            onOrderClick={handleOrderClick}
            onCreateOrder={() => setShowCreateOrder(true)}
          />
        )
      case 'delivery':
        return (
          <DeliveryScreen
            user={user}
            selectedOrder={selectedOrder}
            onBack={() => setSelectedOrder(null)}
          />
        )
      case 'settings':
        return <SettingsScreen user={user} onLogout={onLogout} />
      default:
        return (
          <OrdersScreen
            key={refreshKey}
            user={user}
            onOrderClick={handleOrderClick}
            onCreateOrder={() => setShowCreateOrder(true)}
          />
        )
    }
  }

  return (
    <div className="client-view">
      {renderScreen()}
      {!showCreateOrder && (
        <BottomNavBar activeTab={activeTab} onTabChange={setActiveTab} />
      )}
    </div>
  )
}

export default ClientView

