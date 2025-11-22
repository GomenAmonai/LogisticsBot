import React from 'react'
import './TermsModal.css'
import { CloseIcon } from './Icons'
import { useTheme } from '../contexts/ThemeContext'

const TermsModal = ({ onClose }) => {
  const { theme } = useTheme()

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={`modal-content ${theme}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Условия использования</h2>
          <button className="modal-close" onClick={onClose}>
            <CloseIcon size={24} />
          </button>
        </div>
        
        <div className="modal-body">
          <section>
            <h3>1. Общие положения</h3>
            <p>Платформа предоставляет услуги по организации доставки товаров. Пользователи обязуются соблюдать законодательство и этические нормы.</p>
          </section>

          <section>
            <h3>2. Создание заказов</h3>
            <ul>
              <li>Клиенты могут создавать заказы через WebApp или бота</li>
              <li>Необходимо указывать точную информацию о товаре и адресах</li>
              <li>Запрещено создавать заказы на доставку запрещенных товаров</li>
            </ul>
          </section>

          <section>
            <h3>3. Ответственность</h3>
            <ul>
              <li>Платформа не несет ответственности за содержимое посылок</li>
              <li>Пользователи несут ответственность за достоверность предоставленной информации</li>
              <li>Платформа не гарантирует точное время доставки</li>
            </ul>
          </section>

          <section>
            <h3>4. Связь с менеджером</h3>
            <p>При возникновении вопросов или проблем, используйте кнопку "Связаться с менеджером" в разделе "Доставка".</p>
          </section>

          <section>
            <h3>5. Отмена заказов</h3>
            <p>Заказы могут быть отменены клиентом до начала обработки менеджером. После начала обработки отмена возможна только по согласованию с менеджером.</p>
          </section>

          <section>
            <h3>6. Изменения условий</h3>
            <p>Мы оставляем за собой право изменять условия использования. Пользователи будут уведомлены об изменениях.</p>
          </section>
        </div>

        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>
            Понятно
          </button>
        </div>
      </div>
    </div>
  )
}

export default TermsModal

