/**
 * Módulo para manejar la conversación con la API
 */
class ConversationManager {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.messageCount = 0;
        this.currentAudio = null;
        
        this.initializeEventListeners();
    }

    /**
     * Obtener URL de la API
     */
    getApiUrl() {
        // Detectar si estamos en modo demo
        const urlParams = new URLSearchParams(window.location.search);
        const demoMode = urlParams.get('demo') === 'true';
        
        // En desarrollo, usar localhost
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // Usar puerto 5001 para demo, 5000 para producción
            const port = demoMode ? '5001' : '5000';
            return `http://127.0.0.1:${port}`;
        }
        
        // En producción, usar la misma base URL
        return window.location.origin.replace(/:\d+/, ':5000');
    }

    /**
     * Inicializar event listeners
     */
    initializeEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.loadConversationHistory();
            this.checkApiHealth();
        });
    }

    /**
     * Verificar estado de la API
     */
    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.updateConnectionStatus('connected');
            } else {
                this.updateConnectionStatus('disconnected');
            }
        } catch (error) {
            console.error('Error verificando API:', error);
            this.updateConnectionStatus('disconnected');
        }
    }

    /**
     * Procesar archivo de audio
     */
    async processAudio(audioBlob) {
        try {
            // Mostrar estado de procesamiento
            this.showProcessingStatus(true);
            this.updateConnectionStatus('connecting');

            // Crear FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            console.log('Enviando audio a la API...');

            // Enviar a la API
            const response = await fetch(`${this.apiUrl}/conversation`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            console.log('Respuesta de la API:', data);

            // Agregar mensajes a la conversación
            this.addMessage('user', data.user_message);
            this.addMessage('assistant', data.assistant_message, data.audio_url);

            // Actualizar contador
            this.messageCount = data.conversation_length || this.messageCount + 2;
            this.updateMessageCount();

            // Reproducir audio automáticamente
            if (data.audio_url) {
                setTimeout(() => {
                    this.playAudio(data.audio_url);
                }, 500);
            }

            this.updateConnectionStatus('connected');

        } catch (error) {
            console.error('Error procesando audio:', error);
            this.showError('Error procesando el audio: ' + error.message);
            this.updateConnectionStatus('disconnected');
        } finally {
            this.showProcessingStatus(false);
        }
    }

    /**
     * Agregar mensaje a la conversación
     */
    addMessage(role, content, audioUrl = null) {
        const conversationHistory = document.getElementById('conversationHistory');
        
        // Remover mensaje de bienvenida si existe
        const welcomeMessage = conversationHistory.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Crear elemento del mensaje
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        
        const timestamp = new Date().toLocaleTimeString();
        const icon = role === 'user' ? 'fas fa-user' : 'fas fa-robot';
        const title = role === 'user' ? 'Tú' : 'Asistente IA';

        let audioControls = '';
        if (audioUrl && role === 'assistant') {
            audioControls = `
                <div class="audio-controls">
                    <button class="audio-btn" onclick="conversation.playAudio('${audioUrl}')" title="Reproducir audio">
                        <i class="fas fa-play"></i>
                    </button>
                    <span class="audio-status">Audio disponible</span>
                </div>
            `;
        }

        messageElement.innerHTML = `
            <div class="message-header">
                <i class="${icon}"></i>
                <span>${title}</span>
            </div>
            <div class="message-content">${this.escapeHtml(content)}</div>
            ${audioControls}
            <div class="message-time">${timestamp}</div>
        `;

        conversationHistory.appendChild(messageElement);

        // Scroll al final
        conversationHistory.scrollTop = conversationHistory.scrollHeight;

        // Animación de entrada
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            messageElement.style.transition = 'all 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Reproducir audio
     */
    async playAudio(audioUrl) {
        try {
            // Detener audio actual si existe
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio = null;
            }

            console.log('Reproduciendo audio:', audioUrl);

            // Crear nuevo elemento de audio
            this.currentAudio = new Audio(`${this.apiUrl}${audioUrl}`);
            
            // Event listeners
            this.currentAudio.onplay = () => {
                console.log('Audio iniciado');
                this.updateAudioButtons(true);
            };

            this.currentAudio.onended = () => {
                console.log('Audio terminado');
                this.updateAudioButtons(false);
                this.currentAudio = null;
            };

            this.currentAudio.onerror = (error) => {
                console.error('Error reproduciendo audio:', error);
                this.showError('Error reproduciendo audio');
                this.updateAudioButtons(false);
                this.currentAudio = null;
            };

            // Reproducir
            await this.currentAudio.play();

        } catch (error) {
            console.error('Error reproduciendo audio:', error);
            this.showError('Error reproduciendo audio: ' + error.message);
        }
    }

    /**
     * Actualizar botones de audio
     */
    updateAudioButtons(isPlaying) {
        const audioButtons = document.querySelectorAll('.audio-btn');
        audioButtons.forEach(button => {
            const icon = button.querySelector('i');
            if (isPlaying) {
                icon.className = 'fas fa-pause';
                button.classList.add('playing');
            } else {
                icon.className = 'fas fa-play';
                button.classList.remove('playing');
            }
        });
    }

    /**
     * Cargar historial de conversación
     */
    async loadConversationHistory() {
        try {
            const response = await fetch(`${this.apiUrl}/conversation/history`);
            
            if (!response.ok) {
                console.warn('No se pudo cargar el historial');
                return;
            }

            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                // Limpiar historial actual
                const conversationHistory = document.getElementById('conversationHistory');
                conversationHistory.innerHTML = '';

                // Agregar mensajes del historial
                data.history.forEach(message => {
                    this.addMessage(message.role, message.content);
                });

                this.messageCount = data.total_messages;
                this.updateMessageCount();
            }

        } catch (error) {
            console.error('Error cargando historial:', error);
        }
    }

    /**
     * Limpiar conversación
     */
    async clearConversation() {
        try {
            const response = await fetch(`${this.apiUrl}/conversation/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error limpiando conversación');
            }

            // Limpiar UI
            const conversationHistory = document.getElementById('conversationHistory');
            conversationHistory.innerHTML = `
                <div class="welcome-message">
                    <i class="fas fa-robot"></i>
                    <p>¡Hola! Soy tu asistente de IA. Mantén presionado el botón de micrófono para hablarme.</p>
                </div>
            `;

            this.messageCount = 0;
            this.updateMessageCount();

            console.log('Conversación limpiada');

        } catch (error) {
            console.error('Error limpiando conversación:', error);
            this.showError('Error limpiando la conversación: ' + error.message);
        }
    }

    /**
     * Exportar conversación
     */
    async exportConversation() {
        try {
            const response = await fetch(`${this.apiUrl}/conversation/export`);
            
            if (!response.ok) {
                throw new Error('Error exportando conversación');
            }

            // Crear enlace de descarga
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversacion_${new Date().toISOString().slice(0, 10)}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            console.log('Conversación exportada');

        } catch (error) {
            console.error('Error exportando conversación:', error);
            this.showError('Error exportando la conversación: ' + error.message);
        }
    }

    /**
     * Mostrar/ocultar estado de procesamiento
     */
    showProcessingStatus(show) {
        const processingStatus = document.getElementById('processingStatus');
        if (processingStatus) {
            if (show) {
                processingStatus.classList.remove('hidden');
            } else {
                processingStatus.classList.add('hidden');
            }
        }
    }

    /**
     * Actualizar estado de conexión
     */
    updateConnectionStatus(status) {
        const connectionStatus = document.getElementById('connectionStatus');
        if (connectionStatus) {
            connectionStatus.className = `connection-status ${status}`;
            
            switch (status) {
                case 'connected':
                    connectionStatus.textContent = 'Conectado';
                    break;
                case 'disconnected':
                    connectionStatus.textContent = 'Desconectado';
                    break;
                case 'connecting':
                    connectionStatus.textContent = 'Conectando...';
                    break;
            }
        }
    }

    /**
     * Actualizar contador de mensajes
     */
    updateMessageCount() {
        const messageCountElement = document.getElementById('messageCount');
        if (messageCountElement) {
            messageCountElement.textContent = `${this.messageCount} mensajes`;
        }
    }

    /**
     * Mostrar error
     */
    showError(message) {
        if (window.showError) {
            window.showError(message);
        } else {
            alert(message);
        }
    }

    /**
     * Escapar HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Exportar para uso global
window.ConversationManager = ConversationManager;
