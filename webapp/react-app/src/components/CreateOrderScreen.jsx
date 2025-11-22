import React, { useState } from 'react'
import './CreateOrderScreen.css'
import { createOrder } from '../services/api'

const CreateOrderScreen = ({ user, onBack, onSuccess }) => {
  const [formData, setFormData] = useState({
    description: '',
    from_address: '',
    to_address: '',
    from_contact: '',
    to_contact: '',
    weight: '',
    price: ''
  })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
    // Очищаем ошибку при изменении поля
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      })
    }
  }

  const validate = () => {
    const newErrors = {}
    
    if (!formData.description.trim()) {
      newErrors.description = 'Описание обязательно'
    }
    if (!formData.from_address.trim()) {
      newErrors.from_address = 'Адрес отправления обязателен'
    }
    if (!formData.to_address.trim()) {
      newErrors.to_address = 'Адрес доставки обязателен'
    }
    if (!formData.from_contact.trim()) {
      newErrors.from_contact = 'Контакт отправителя обязателен'
    }
    if (!formData.to_contact.trim()) {
      newErrors.to_contact = 'Контакт получателя обязателен'
    }
    if (!formData.weight || parseFloat(formData.weight) <= 0) {
      newErrors.weight = 'Введите корректный вес'
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      newErrors.price = 'Введите корректную цену'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validate()) {
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('Пожалуйста, заполните все обязательные поля')
      }
      return
    }

    try {
      setSubmitting(true)
      const orderData = {
        ...formData,
        weight: parseFloat(formData.weight),
        price: parseFloat(formData.price)
      }
      
      const response = await createOrder(orderData)
      
      // Проверяем ответ на ошибки
      if (response.error) {
        throw new Error(response.error)
      }
      
      if (!response.success && !response.order) {
        throw new Error('Не удалось создать заказ')
      }
      
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert('✅ Заказ успешно создан!')
      }
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      console.error('Ошибка создания заказа:', error)
      const errorMessage = error.message || 'Ошибка создания заказа. Попробуйте позже.'
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(errorMessage)
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="create-order-screen">
      <div className="create-order-header">
        <button className="back-button" onClick={onBack}>
          ← Назад
        </button>
        <h1>Оформить заказ</h1>
      </div>

      <div className="create-order-content">
        <form onSubmit={handleSubmit}>
          {/* Описание */}
          <div className="form-section">
            <h3>📝 Описание заказа</h3>
            <div className="form-group">
              <label>Что доставить? <span className="required">*</span></label>
              <textarea
                className={`form-input ${errors.description ? 'error' : ''}`}
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Опишите что нужно доставить, размеры, особенности..."
                rows={4}
              />
              {errors.description && (
                <span className="error-message">{errors.description}</span>
              )}
            </div>
          </div>

          {/* Адреса */}
          <div className="form-section">
            <h3>📍 Адреса</h3>
            <div className="form-group">
              <label>Откуда (адрес отправления) <span className="required">*</span></label>
              <input
                type="text"
                className={`form-input ${errors.from_address ? 'error' : ''}`}
                name="from_address"
                value={formData.from_address}
                onChange={handleChange}
                placeholder="Город, улица, дом, квартира"
              />
              {errors.from_address && (
                <span className="error-message">{errors.from_address}</span>
              )}
            </div>

            <div className="form-group">
              <label>Куда (адрес доставки) <span className="required">*</span></label>
              <input
                type="text"
                className={`form-input ${errors.to_address ? 'error' : ''}`}
                name="to_address"
                value={formData.to_address}
                onChange={handleChange}
                placeholder="Город, улица, дом, квартира"
              />
              {errors.to_address && (
                <span className="error-message">{errors.to_address}</span>
              )}
            </div>
          </div>

          {/* Контакты */}
          <div className="form-section">
            <h3>📞 Контакты</h3>
            <div className="form-group">
              <label>Контакт отправителя <span className="required">*</span></label>
              <input
                type="text"
                className={`form-input ${errors.from_contact ? 'error' : ''}`}
                name="from_contact"
                value={formData.from_contact}
                onChange={handleChange}
                placeholder="Телефон и/или имя"
              />
              {errors.from_contact && (
                <span className="error-message">{errors.from_contact}</span>
              )}
            </div>

            <div className="form-group">
              <label>Контакт получателя <span className="required">*</span></label>
              <input
                type="text"
                className={`form-input ${errors.to_contact ? 'error' : ''}`}
                name="to_contact"
                value={formData.to_contact}
                onChange={handleChange}
                placeholder="Телефон и/или имя"
              />
              {errors.to_contact && (
                <span className="error-message">{errors.to_contact}</span>
              )}
            </div>
          </div>

          {/* Параметры */}
          <div className="form-section">
            <h3>⚖️ Параметры</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Вес (кг) <span className="required">*</span></label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  className={`form-input ${errors.weight ? 'error' : ''}`}
                  name="weight"
                  value={formData.weight}
                  onChange={handleChange}
                  placeholder="0.0"
                />
                {errors.weight && (
                  <span className="error-message">{errors.weight}</span>
                )}
              </div>

              <div className="form-group">
                <label>Цена (₽) <span className="required">*</span></label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  className={`form-input ${errors.price ? 'error' : ''}`}
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  placeholder="0.00"
                />
                {errors.price && (
                  <span className="error-message">{errors.price}</span>
                )}
              </div>
            </div>
          </div>

          {/* Кнопки */}
          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onBack}
              disabled={submitting}
            >
              Отмена
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? '⏳ Создание...' : '✅ Создать заказ'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateOrderScreen

