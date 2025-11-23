import React from 'react'
import './UserInfoBar.css'

const roleLabels = {
  client: 'Клиент',
  manager: 'Менеджер',
  admin: 'Администратор'
}

const UserInfoBar = ({ user, onLogout }) => {
  if (!user) return null
  return (
    <div className="user-info-bar">
      <div>
        <div className="user-info-name">{user.name || user.first_name || 'Без имени'}</div>
        <div className="user-info-meta">
          ID: {user.id || user.user_id} • Роль: {roleLabels[user.role] || user.role}
        </div>
      </div>
      {onLogout && (
        <button className="btn btn-secondary btn-small" onClick={onLogout}>
          Выйти
        </button>
      )}
    </div>
  )
}

export default UserInfoBar

