const API_BASE = import.meta.env.VITE_API_URL || window.location.origin

export const authUser = async (initData) => {
  const response = await fetch(`${API_BASE}/auth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ initData })
  })
  return response.json()
}

export const getCurrentUser = async () => {
  const response = await fetch(`${API_BASE}/api/user`)
  return response.json()
}

export const getOrders = async (options = {}) => {
  let url = `${API_BASE}/api/orders`
  if (typeof options === 'string' && options) {
    url += `?type=${options}`
  } else if (options && options.type) {
    const params = new URLSearchParams({ type: options.type })
    url += `?${params.toString()}`
  }
  const response = await fetch(url)
  return response.json()
}

export const createOrder = async (orderData) => {
  const response = await fetch(`${API_BASE}/api/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderData)
  })
  
  const data = await response.json()
  
  // Проверяем статус ответа
  if (!response.ok) {
    throw new Error(data.error || 'Ошибка создания заказа')
  }
  
  return data
}

export const getOrder = async (orderId) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}`)
  return response.json()
}

export const updateOrderStatus = async (orderId, status) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  })
  return response.json()
}

export const getTickets = async (status) => {
  const url = status 
    ? `${API_BASE}/api/tickets?status=${status}`
    : `${API_BASE}/api/tickets`
  const response = await fetch(url)
  return response.json()
}

export const acceptTicket = async (ticketId) => {
  const response = await fetch(`${API_BASE}/api/tickets/${ticketId}/accept`, {
    method: 'POST'
  })
  return response.json()
}

export const getStats = async () => {
  const response = await fetch(`${API_BASE}/api/stats`)
  return response.json()
}

export const createPayment = async (paymentData) => {
  const response = await fetch(`${API_BASE}/api/payments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(paymentData)
  })
  return response.json()
}

export const updateUserProfile = async (profileData) => {
  const response = await fetch(`${API_BASE}/api/user`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profileData)
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Ошибка обновления профиля')
  }
  
  return response.json()
}

export const getOrderTracking = async (orderId) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/tracking`)
  return response.json()
}

export const contactLogist = async (orderId) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/contact-logist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  return response.json()
}

export const getChatMessages = async (orderId) => {
  const response = await fetch(`${API_BASE}/api/chat/${orderId}`)
  return response.json()
}

export const sendChatMessage = async (orderId, message) => {
  const response = await fetch(`${API_BASE}/api/chat/${orderId}/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  return response.json()
}

export const assignOrder = async (orderId) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/assign`, {
    method: 'POST'
  })
  return response.json()
}

export const createOrderOffer = async (orderId, payload) => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/offer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return response.json()
}

export const respondToOffer = async (orderId, decision = 'accept') => {
  const response = await fetch(`${API_BASE}/api/orders/${orderId}/accept-offer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision })
  })
  return response.json()
}

