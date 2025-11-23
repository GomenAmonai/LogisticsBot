import React, { useState } from 'react'
import './AdminTestPanel.css'
import { adminBootstrapData, adminClearData, adminCreateTestUser } from '../services/api'

const AdminTestPanel = () => {
  const [creating, setCreating] = useState(false)
  const [userForm, setUserForm] = useState({
    user_id: '',
    username: '',
    first_name: '',
    role: 'client'
  })
  const [message, setMessage] = useState('')

  const handleBootstrap = async () => {
    setMessage('Создание демо-данных...')
    const response = await adminBootstrapData()
    if (response.success) {
      setMessage(`Готово. Клиент: ${response.data.client_id}, менеджер: ${response.data.manager_id}`)
    } else {
      setMessage(response.error || 'Ошибка')
    }
  }

  const handleClear = async () => {
    setMessage('Очистка таблиц...')
    const response = await adminClearData()
    setMessage(response.success ? 'Данные очищены' : response.error || 'Ошибка')
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setCreating(true)
    setMessage('Создание пользователя...')
    const response = await adminCreateTestUser({
      ...userForm,
      user_id: userForm.user_id || undefined
    })
    if (response.success) {
      setMessage(`Создан пользователь ${response.user_id} (${response.role})`)
      setUserForm({ user_id: '', username: '', first_name: '', role: 'client' })
    } else {
      setMessage(response.error || 'Ошибка')
    }
    setCreating(false)
  }

  return (
    <div className="admin-test-panel">
      <h2>🧪 Тест-панель</h2>
      <p>Используйте эти действия для подготовки окружения перед тестом.</p>

      <div className="admin-test-actions">
        <button className="btn btn-primary" onClick={handleBootstrap}>
          Создать демо-данные
        </button>
        <button className="btn btn-secondary" onClick={handleClear}>
          Очистить таблицы
        </button>
      </div>

      <form className="admin-test-form" onSubmit={handleCreateUser}>
        <h3>Создать тестового пользователя</h3>
        <div className="form-row">
          <input
            type="text"
            placeholder="user_id (опционально)"
            value={userForm.user_id}
            onChange={(e) => setUserForm({ ...userForm, user_id: e.target.value })}
          />
          <select
            value={userForm.role}
            onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
          >
            <option value="client">client</option>
            <option value="manager">manager</option>
            <option value="admin">admin</option>
          </select>
        </div>
        <div className="form-row">
          <input
            type="text"
            placeholder="username"
            value={userForm.username}
            onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
          />
          <input
            type="text"
            placeholder="Имя"
            value={userForm.first_name}
            onChange={(e) => setUserForm({ ...userForm, first_name: e.target.value })}
          />
        </div>
        <button className="btn btn-primary" type="submit" disabled={creating}>
          {creating ? 'Создание...' : 'Создать пользователя'}
        </button>
      </form>

      {message && <div className="admin-test-message">{message}</div>}
    </div>
  )
}

export default AdminTestPanel

