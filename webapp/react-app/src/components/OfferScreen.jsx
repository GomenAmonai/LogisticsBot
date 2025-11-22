import React, { useEffect, useState } from 'react'
import './OfferScreen.css'
import { getOrder, respondToOffer } from '../services/api'
import { BackIcon } from './Icons'

const OfferScreen = ({ order, onBack, onDecision }) => {
  const [currentOrder, setCurrentOrder] = useState(order)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    if (!order?.id) return
    const load = async () => {
      try {
        setLoading(true)
        const data = await getOrder(order.id)
        setCurrentOrder(data.order || order)
      } catch (error) {
        console.error('Ошибка загрузки оферты:', error)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [order?.id])

  const handleDecision = async (decision) => {
    if (!currentOrder?.offer_status || processing) return
    try {
      setProcessing(true)
      await respondToOffer(currentOrder.id, decision)
      setCurrentOrder((prev) =>
        prev
          ? {
              ...prev,
              offer_status: decision === 'accept' ? 'accepted' : 'rejected'
            }
          : prev
      )
      if (onDecision) {
        onDecision(decision)
      }
    } catch (error) {
      console.error('Ошибка ответа на оферту:', error)
    } finally {
      setProcessing(false)
    }
  }

  if (!order) {
    return null
  }

  const offer = currentOrder || order

  return (
    <div className="offer-screen">
      <div className="offer-header">
        {onBack && (
          <button className="back-button" onClick={onBack}>
            <BackIcon size={18} />
            Назад
          </button>
        )}
        <h1>Оферта логиста</h1>
      </div>

      {loading && !offer.offer_status ? (
        <div className="offer-card loading">Загрузка оферты...</div>
      ) : offer.offer_status === 'draft' || !offer.offer_status ? (
        <div className="offer-card empty">
          <p>Оферта пока не сформирована. Логист сообщит, когда она будет готова.</p>
        </div>
      ) : (
        <div className="offer-card">
          <div className="offer-status">{offer.offer_status}</div>
          <div className="offer-row">
            <span>Стоимость</span>
            <strong>
              {offer.offer_price} {offer.offer_currency || 'RUB'}
            </strong>
          </div>
          <div className="offer-row">
            <span>Срок доставки</span>
            <strong>{offer.offer_delivery_days} дн.</strong>
          </div>
          {offer.offer_comment && (
            <div className="offer-comment">
              <span>Комментарий</span>
              <p>{offer.offer_comment}</p>
            </div>
          )}
          {offer.offer_status === 'sent' && (
            <div className="offer-actions">
              <button
                className="btn btn-secondary"
                onClick={() => handleDecision('reject')}
                disabled={processing}
              >
                Отклонить
              </button>
              <button
                className="btn btn-primary"
                onClick={() => handleDecision('accept')}
                disabled={processing}
              >
                Принять
              </button>
            </div>
          )}
          {offer.offer_status === 'accepted' && (
            <div className="offer-note success">Вы приняли условия оферты. Логист уже в пути 🚚</div>
          )}
          {offer.offer_status === 'rejected' && (
            <div className="offer-note danger">Вы отклонили оферту. Свяжитесь с логистом для уточнения.</div>
          )}
        </div>
      )}
    </div>
  )
}

export default OfferScreen

