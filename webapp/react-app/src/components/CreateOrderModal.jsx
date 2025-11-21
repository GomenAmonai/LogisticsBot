import React, { useState } from 'react'
import './CreateOrderModal.css'

const CreateOrderModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    description: '',
    from_address: '',
    to_address: '',
    from_contact: '',
    to_contact: '',
    weight: '',
    price: ''
  })

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      weight: parseFloat(formData.weight) || 0,
      price: parseFloat(formData.price) || 0
    })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Создать заказ</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Описание заказа</label>
            <textarea
              className="form-textarea"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              placeholder="Опишите что нужно доставить"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Откуда (адрес)</label>
              <input
                className="form-input"
                type="text"
                name="from_address"
                value={formData.from_address}
                onChange={handleChange}
                required
                placeholder="Адрес отправления"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Куда (адрес)</label>
              <input
                className="form-input"
                type="text"
                name="to_address"
                value={formData.to_address}
                onChange={handleChange}
                required
                placeholder="Адрес доставки"
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Контакт отправителя</label>
              <input
                className="form-input"
                type="text"
                name="from_contact"
                value={formData.from_contact}
                onChange={handleChange}
                required
                placeholder="Телефон/имя"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Контакт получателя</label>
              <input
                className="form-input"
                type="text"
                name="to_contact"
                value={formData.to_contact}
                onChange={handleChange}
                required
                placeholder="Телефон/имя"
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Вес (кг)</label>
              <input
                className="form-input"
                type="number"
                step="0.1"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                required
                placeholder="0.0"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Цена (₽)</label>
              <input
                className="form-input"
                type="number"
                step="0.01"
                name="price"
                value={formData.price}
                onChange={handleChange}
                required
                placeholder="0.00"
              />
            </div>
          </div>
          
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn btn-primary">
              Создать заказ
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateOrderModal

