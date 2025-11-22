import React, { useState } from 'react'
import './ClientView.css'
import BottomNavBar from './BottomNavBar'
import OrdersScreen from './OrdersScreen'
import ProfileScreen from './ProfileScreen'
import DeliveryScreen from './DeliveryScreen'
import SettingsScreen from './SettingsScreen'

const ClientView = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('home')

  const renderScreen = () => {
    switch (activeTab) {
      case 'home':
        return <OrdersScreen user={user} />
      case 'profile':
        return <ProfileScreen user={user} />
      case 'orders':
        return <OrdersScreen user={user} />
      case 'delivery':
        return <DeliveryScreen user={user} />
      case 'settings':
        return <SettingsScreen user={user} onLogout={onLogout} />
      default:
        return <OrdersScreen user={user} />
    }
  }

  return (
    <div className="client-view">
      {renderScreen()}
      <BottomNavBar activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  )
}

export default ClientView

