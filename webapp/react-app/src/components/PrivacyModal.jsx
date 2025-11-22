import React from 'react'
import './PrivacyModal.css'
import { CloseIcon } from './Icons'
import { useTheme } from '../contexts/ThemeContext'

const PrivacyModal = ({ onClose }) => {
  const { theme } = useTheme()

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={`modal-content ${theme}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Политика конфиденциальности</h2>
          <button className="modal-close" onClick={onClose}>
            <CloseIcon size={24} />
          </button>
        </div>
        
        <div className="modal-body">
          <section>
            <h3>1. Сбор данных</h3>
            <p>Мы собираем следующие данные:</p>
            <ul>
              <li>Ваш Telegram ID</li>
              <li>Имя и фамилия</li>
              <li>Username (если указан)</li>
              <li>Данные о заказах и доставках</li>
              <li>Контактная информация (телефон, email)</li>
            </ul>
          </section>

          <section>
            <h3>2. Использование данных</h3>
            <p>Ваши данные используются для:</p>
            <ul>
              <li>Обработки заказов</li>
              <li>Связи с вами по вопросам доставки</li>
              <li>Улучшения качества сервиса</li>
              <li>Отправки уведомлений о статусе заказов (при включенной настройке)</li>
            </ul>
          </section>

          <section>
            <h3>3. Защита данных</h3>
            <p>Все данные хранятся в защищенной базе данных и не передаются третьим лицам без вашего согласия. Мы используем современные методы шифрования для защиты вашей информации.</p>
          </section>

          <section>
            <h3>4. Ваши права</h3>
            <p>Вы имеете право:</p>
            <ul>
              <li>Запросить информацию о ваших данных</li>
              <li>Удалить ваши данные</li>
              <li>Отозвать согласие на обработку данных</li>
              <li>Отключить уведомления в любое время</li>
            </ul>
          </section>

          <section>
            <h3>5. Контакты</h3>
            <p>По вопросам конфиденциальности обращайтесь: support@logistics.com</p>
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

export default PrivacyModal

