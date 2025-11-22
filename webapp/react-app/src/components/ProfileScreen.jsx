import React, { useState, useEffect } from 'react'
import './ProfileScreen.css'
import { getCurrentUser, updateUserProfile } from '../services/api'

const ProfileScreen = ({ user }) => {
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    username: '',
    phone: '',
    email: ''
  })
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadProfile()
  }, [user])

  const loadProfile = async () => {
    try {
      setLoading(true)
      const data = await getCurrentUser()
      setProfile({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        username: data.username || '',
        phone: data.phone || '',
        email: data.email || ''
      })
    } catch (error) {
      console.error('Ошибка загрузки профиля:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value
    })
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await updateUserProfile(profile)
      setEditing(false)
      
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Профиль успешно обновлен!')
      }
    } catch (error) {
      console.error('Ошибка сохранения профиля:', error)
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Ошибка сохранения профиля')
      }
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="profile-screen">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="profile-screen">
      <div className="profile-header">
        <div className="profile-avatar">
          {profile.first_name?.[0]?.toUpperCase() || '👤'}
        </div>
        <h2>{profile.first_name || 'Пользователь'}</h2>
        <p className="profile-role">Клиент</p>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h3>Личная информация</h3>
          
          <div className="form-group">
            <label>Имя</label>
            <input
              type="text"
              name="first_name"
              value={profile.first_name}
              onChange={handleChange}
              disabled={!editing}
              className={editing ? 'editing' : ''}
            />
          </div>

          <div className="form-group">
            <label>Фамилия</label>
            <input
              type="text"
              name="last_name"
              value={profile.last_name}
              onChange={handleChange}
              disabled={!editing}
              className={editing ? 'editing' : ''}
            />
          </div>

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={profile.username}
              onChange={handleChange}
              disabled={!editing}
              className={editing ? 'editing' : ''}
            />
          </div>

          <div className="form-group">
            <label>Телефон</label>
            <input
              type="tel"
              name="phone"
              value={profile.phone}
              onChange={handleChange}
              disabled={!editing}
              className={editing ? 'editing' : ''}
              placeholder="+7 (999) 123-45-67"
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleChange}
              disabled={!editing}
              className={editing ? 'editing' : ''}
              placeholder="example@mail.com"
            />
          </div>
        </div>

        <div className="profile-actions">
          {!editing ? (
            <button
              className="btn btn-primary"
              onClick={() => setEditing(true)}
            >
              ✏️ Редактировать профиль
            </button>
          ) : (
            <div className="edit-actions">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setEditing(false)
                  loadProfile()
                }}
                disabled={saving}
              >
                Отмена
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Сохранение...' : '💾 Сохранить'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProfileScreen

