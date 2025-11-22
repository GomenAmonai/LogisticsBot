import React, { useEffect, useRef, useState } from 'react'
import './ChatScreen.css'
import { getChatMessages, sendChatMessage } from '../services/api'
import { BackIcon } from './Icons'

const ChatScreen = ({ order, user, onBack }) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (!order?.id) {
      return
    }
    loadMessages()
    const interval = setInterval(() => loadMessages(true), 5000)
    return () => clearInterval(interval)
  }, [order?.id])

  const loadMessages = async (silent = false) => {
    if (!order?.id) return
    try {
      if (!silent) {
        setLoading(true)
      }
      const data = await getChatMessages(order.id)
      setMessages(data.messages || [])
    } catch (error) {
      console.error('Ошибка загрузки чата:', error)
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || sending) {
      return
    }
    try {
      setSending(true)
      await sendChatMessage(order.id, inputValue.trim())
      setInputValue('')
      await loadMessages()
    } catch (error) {
      console.error('Ошибка отправки сообщения:', error)
    } finally {
      setSending(false)
    }
  }

  if (!order) {
    return null
  }

  return (
    <div className="chat-screen">
      <div className="chat-header">
        {onBack && (
          <button className="chat-back" onClick={onBack}>
            <BackIcon size={18} />
            Назад
          </button>
        )}
        <div>
          <div className="chat-title">Заказ #{order.id}</div>
          <div className="chat-subtitle">{order.description || 'Без описания'}</div>
        </div>
      </div>

      <div className="chat-messages">
        {loading && messages.length === 0 ? (
          <div className="chat-placeholder">Загрузка сообщений...</div>
        ) : messages.length === 0 ? (
          <div className="chat-placeholder">Сообщений пока нет. Напишите первым!</div>
        ) : (
          messages.map((msg) => {
            const isOwn = msg.sender_id === user?.id || msg.sender_id === user?.user_id
            return (
              <div
                key={msg.id}
                className={`chat-bubble ${isOwn ? 'own' : 'remote'}`}
              >
                <div className="chat-message">{msg.message}</div>
                <div className="chat-meta">
                  <span>{msg.sender_role}</span>
                  <span>
                    {new Date(msg.created_at).toLocaleTimeString('ru-RU', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            )
          })
        )}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Сообщение..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button type="submit" disabled={sending || !inputValue.trim()}>
          Отправить
        </button>
      </form>
    </div>
  )
}

export default ChatScreen

