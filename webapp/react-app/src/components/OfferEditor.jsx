import React, { useState } from 'react'
import './OfferEditor.css'
import { createOrderOffer } from '../services/api'
import { BackIcon } from './Icons'

const OfferEditor = ({ order, onBack, onSuccess }) => {
  const [formData, setFormData] = useState({
    offer_price: order?.offer_price || '',
    offer_currency: order?.offer_currency || 'RUB',
    offer_delivery_days: order?.offer_delivery_days || '',
    offer_comment: order?.offer_comment || ''
  })
  const [saving, setSaving] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!order?.id) return
    try {
      setSaving(true)
      const payload = {
        offer_price: parseFloat(formData.offer_price),
        offer_currency: (formData.offer_currency || 'RUB').toUpperCase(),
        offer_delivery_days: parseInt(formData.offer_delivery_days, 10),
        offer_comment: formData.offer_comment
      }
      const response = await createOrderOffer(order.id, payload)
      if (onSuccess) {
        onSuccess(response.order)
      }
    } catch (error) {
      console.error('Ошибка сохранения оферты:', error)
    } finally {
      setSaving(false)
    }
  }

  if (!order) return null

  return (
    <div className="offer-editor">
      <div className="offer-header">
        {onBack && (
          <button className="back-button" onClick={onBack}>
            <BackIcon size={18} />
            Назад
          </button>
        )}
        <div>
          <h1>Оферта для заказа #{order.id}</h1>
          <p>{order.description || 'Без описания'}</p>
        </div>
      </div>

      <form className="offer-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Стоимость</label>
            <input
              type="number"
              step="0.01"
              name="offer_price"
              value={formData.offer_price}
              onChange={handleChange}
              required
              placeholder="0.00"
            />
          </div>
          <div className="form-group">
            <label>Валюта</label>
            <input
              type="text"
              name="offer_currency"
              value={formData.offer_currency}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Срок доставки (дни)</label>
          <input
            type="number"
            min="1"
            name="offer_delivery_days"
            value={formData.offer_delivery_days}
            onChange={handleChange}
            required
            placeholder="Например, 5"
          />
        </div>

        <div className="form-group">
          <label>Комментарий для клиента</label>
          <textarea
            name="offer_comment"
            value={formData.offer_comment}
            onChange={handleChange}
            rows={4}
            placeholder="Описание услуг, условия оплаты и т.д."
          />
        </div>

        <div className="offer-actions">
          <button type="button" className="btn btn-secondary" onClick={onBack} disabled={saving}>
            Отмена
          </button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Отправка...' : 'Отправить оферту'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default OfferEditor

