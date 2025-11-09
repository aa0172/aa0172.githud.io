// chat.js - Основные функции для работы чата

class GymFriendChat {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    // Инициализация WebSocket соединения
    connect(roomName) {
        if (this.socket) {
            this.disconnect();
        }

        this.currentRoom = roomName;
        this.socket = new WebSocket(
            `ws://${window.location.host}/ws/chat/${roomName}/`
        );

        this.socket.onopen = () => {
            console.log('WebSocket connection established');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.showConnectionStatus('connected');
        };

        this.socket.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket connection closed');
            this.isConnected = false;
            this.showConnectionStatus('disconnected');

            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.connect(roomName);
                }, 3000 * this.reconnectAttempts);
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showConnectionStatus('error');
        };
    }

    // Отправка сообщения
    sendMessage(message, username, userId) {
        if (this.isConnected && this.socket) {
            this.socket.send(JSON.stringify({
                type: 'chat_message',
                message: message,
                username: username,
                user_id: userId
            }));
            return true;
        } else {
            this.showNotification('Ошибка соединения', 'error');
            return false;
        }
    }

    // Обработка входящих сообщений
    handleMessage(data) {
        switch(data.type) {
            case 'chat_message':
                this.displayMessage(data);
                break;
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
                break;
            case 'user_list_update':
                this.updateUserList(data.users);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    // Отображение сообщения в чате
    displayMessage(data) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const messageElement = this.createMessageElement(data);
        chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    // Создание элемента сообщения
    createMessageElement(data) {
        const messageDiv = document.createElement('div');
        const isOwn = data.user_id == window.userId;

        messageDiv.className = `message ${isOwn ? 'own-message' : ''}`;
        messageDiv.setAttribute('data-message-id', data.message_id);

        const timestamp = data.timestamp || new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="flex-center">
                    <strong>${this.escapeHtml(data.username)}</strong>
                    ${isOwn ? '<span class="user-badge">Вы</span>' : ''}
                </div>
                <span>${timestamp}</span>
            </div>
            <div class="message-content">${this.escapeHtml(data.message)}</div>
        `;

        return messageDiv;
    }

    // Обработка подключения пользователя
    handleUserJoined(data) {
        this.displaySystemMessage(`${data.username} присоединился к чату`);
        this.updateOnlineCount(data.user_count);
    }

    // Обработка отключения пользователя
    handleUserLeft(data) {
        this.displaySystemMessage(`${data.username} покинул чат`);
        this.updateOnlineCount(data.user_count);
    }

    // Отображение системного сообщения
    displaySystemMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const systemMessage = document.createElement('div');
        systemMessage.className = 'message system-message';
        systemMessage.innerHTML = `<div>${this.escapeHtml(message)}</div>`;

        chatMessages.appendChild(systemMessage);
        this.scrollToBottom();
    }

    // Обновление счетчика онлайн пользователей
    updateOnlineCount(count) {
        const countElement = document.getElementById('user-count');
        if (countElement) {
            countElement.textContent = count;
        }
    }

    // Обновление списка пользователей
    updateUserList(users) {
        const usersList = document.getElementById('online-users-list');
        if (!usersList) return;

        usersList.innerHTML = '';

        users.forEach(user => {
            const userElement = this.createUserElement(user);
            usersList.appendChild(userElement);
        });
    }

    // Создание элемента пользователя
    createUserElement(user) {
        const userDiv = document.createElement('div');
        userDiv.className = 'online-user';

        const avatarHtml = user.avatar ?
            `<img src="${user.avatar}" alt="Аватар" class="avatar-sm">` :
            `<div class="avatar-placeholder avatar-sm">${user.username.charAt(0).toUpperCase()}</div>`;

        userDiv.innerHTML = `
            <div class="flex-center" style="gap: 0.75rem;">
                ${avatarHtml}
                <div>
                    <strong>${this.escapeHtml(user.username)}</strong>
                    <div class="online-status">🟢 онлайн</div>
                </div>
            </div>
        `;

        return userDiv;
    }

    // Прокрутка к последнему сообщению
    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Отображение статуса соединения
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;

        const statusMessages = {
            connected: '🟢 Подключено',
            disconnected: '🔴 Отключено',
            error: '⚠️ Ошибка соединения'
        };

        statusElement.textContent = statusMessages[status] || '❓ Неизвестно';
        statusElement.className = `connection-status ${status}`;
    }

    // Отображение уведомления
    showNotification(message, type = 'info') {
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            <span class="alert-close" onclick="this.parentElement.remove()">×</span>
            ${message}
        `;

        // Добавляем в контейнер уведомлений
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }

        container.appendChild(notification);

        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Экранирование HTML
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Отключение от чата
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.isConnected = false;
    }

    // Загрузка истории сообщений
    async loadMessageHistory(roomId, lastMessageId = 0) {
        try {
            const response = await fetch(`/chat/api/messages/${roomId}/?last_message_id=${lastMessageId}`);
            const data = await response.json();

            if (data.messages) {
                data.messages.forEach(message => {
                    this.displayMessage(message);
                });
            }
        } catch (error) {
            console.error('Error loading message history:', error);
        }
    }
}

// Глобальный экземпляр чата
window.gymFriendChat = new GymFriendChat();

// Инициализация чата при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Автофокус на поле ввода сообщения
    const messageInput = document.getElementById('chat-message-input');
    if (messageInput) {
        messageInput.focus();

        // Отправка сообщения по Enter
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const submitBtn = document.getElementById('chat-message-submit');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });
    }

    // Обработчик отправки сообщения
    const submitBtn = document.getElementById('chat-message-submit');
    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            const messageInput = document.getElementById('chat-message-input');
            if (messageInput && messageInput.value.trim()) {
                const success = window.gymFriendChat.sendMessage(
                    messageInput.value.trim(),
                    window.userName,
                    window.userId
                );

                if (success) {
                    messageInput.value = '';
                }
            }
        });
    }

    // Прокрутка к низу при загрузке страницы чата
    if (document.getElementById('chat-messages')) {
        window.gymFriendChat.scrollToBottom();
    }
});

// Функции для работы с локальным хранилищем
const StorageManager = {
    set: function(key, value) {
        try {
            localStorage.setItem(`gymfriend_${key}`, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage is not available');
        }
    },

    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`gymfriend_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            return defaultValue;
        }
    },

    remove: function(key) {
        try {
            localStorage.removeItem(`gymfriend_${key}`);
        } catch (e) {
            console.warn('LocalStorage is not available');
        }
    }
};

// Утилиты для дат и времени
const DateUtils = {
    formatTime: function(date) {
        return new Date(date).toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    formatDate: function(date) {
        return new Date(date).toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    isToday: function(date) {
        const today = new Date();
        const compareDate = new Date(date);
        return today.toDateString() === compareDate.toDateString();
    }
};