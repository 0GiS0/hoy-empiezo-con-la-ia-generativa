/**
 * 🎤 Cliente OpenAI Realtime API usando WebRTC
 * Basado en el ejemplo oficial de OpenAI: https://platform.openai.com/docs/guides/realtime
 */

/**
 * Escapes HTML special characters in a string to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escapeHTML(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

class OpenAIRealtimeClient {
    constructor() {
        // Estado de la aplicación
        this.isSessionActive = false;
        this.isConnecting = false;
        this.events = [];
        this.dataChannel = null;
        this.peerConnection = null;
        this.audioElement = null;
        
        // Configuración
        this.config = {
            // URL del servidor local para obtener ephemeral keys
            get tokenUrl() {
                const protocol = window.location.protocol === 'https:' ? 'https://' : 'http://';
                const host = window.location.hostname;
                const port = window.location.port || 8000; // Usar el puerto actual o 8000 por defecto
                return `${protocol}${host}:${port}/api/token`;
            },
            // OpenAI Realtime API configuration
            openai: {
                baseUrl: "https://api.openai.com/v1/realtime",
                model: "gpt-4o-realtime-preview-2024-12-17"
            }
        };
        
        // Elementos del DOM
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            connectionStatus: document.getElementById('connectionStatus'),
            statusText: document.getElementById('statusText'),
            volumeFill: document.getElementById('volumeFill'),
            volumeText: document.getElementById('volumeText'),
            connectionState: document.getElementById('connectionState'),
            bytesSent: document.getElementById('bytesSent'),
            packetsSent: document.getElementById('packetsSent'),
            latency: document.getElementById('latency'),
            logContainer: document.getElementById('logContainer'),
            sampleRate: document.getElementById('sampleRate'),
            bitrate: document.getElementById('bitrate'),
            textInput: document.getElementById('textInput'),
            sendTextBtn: document.getElementById('sendTextBtn'),
            chatMessages: document.getElementById('chatMessages'),
            logPanel: document.getElementById('logPanel'),
            logToggleBtn: document.getElementById('logToggleBtn'),
            clearLogsBtn: document.getElementById('clearLogsBtn')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupLogPanel();
        this.updateUI();
        this.clearWelcomeMessage();
        this.log('🎤 Cliente OpenAI Realtime inicializado', 'info');
        this.log('💡 Basado en el ejemplo oficial de OpenAI con WebRTC', 'info');
    }
    
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startSession());
        this.elements.stopBtn.addEventListener('click', () => this.stopSession());
        
        // Text input functionality
        this.elements.sendTextBtn.addEventListener('click', () => this.handleTextInput());
        this.elements.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleTextInput();
            }
        });
        
        // Detectar cambios en la configuración
        this.elements.sampleRate.addEventListener('change', () => {
            if (this.isSessionActive) {
                this.log('⚠️ Configuración cambiada, reiniciando sesión...', 'warning');
                this.stopSession();
                setTimeout(() => this.startSession(), 1000);
            }
        });
    }
    
    /**
     * 📋 Configurar panel de logs
     */
    setupLogPanel() {
        // Toggle panel de logs
        this.elements.logToggleBtn.addEventListener('click', () => {
            const isHidden = this.elements.logPanel.classList.contains('hidden');
            if (isHidden) {
                this.elements.logPanel.classList.remove('hidden');
                this.elements.logToggleBtn.classList.add('active');
                this.elements.logToggleBtn.title = 'Ocultar logs';
            } else {
                this.elements.logPanel.classList.add('hidden');
                this.elements.logToggleBtn.classList.remove('active');
                this.elements.logToggleBtn.title = 'Mostrar logs';
            }
        });
        
        // Limpiar logs
        this.elements.clearLogsBtn.addEventListener('click', () => {
            this.clearLogs();
        });
    }
    
    /**
     * 🗑️ Limpiar todos los logs
     */
    clearLogs() {
        if (this.elements.logContainer) {
            this.elements.logContainer.innerHTML = '';
            this.log('🧹 Logs limpiados', 'info');
        }
    }
    
    /**
     * 🗨️ Limpiar mensaje de bienvenida al iniciar conversación
     */
    clearWelcomeMessage() {
        const welcomeMessage = this.elements.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage && this.elements.chatMessages.children.length > 1) {
            welcomeMessage.remove();
        }
    }
    
    /**
     * 💬 Agregar mensaje al chat
     */
    addMessage(content, isUser = false) {
        this.clearWelcomeMessage();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;
        
        messageDiv.appendChild(bubbleDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        
        // Scroll al final
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * ⏳ Mostrar indicador de escritura
     */
    showTypingIndicator() {
        this.hideTypingIndicator(); // Eliminar indicador previo
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-message';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(typingDiv);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * 🚫 Ocultar indicador de escritura
     */
    hideTypingIndicator() {
        const typingMessage = this.elements.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }
    
    /**
     * 🚀 Inicia una nueva sesión con OpenAI Realtime API
     */
    async startSession() {
        if (this.isConnecting || this.isSessionActive) {
            this.log('⚠️ Ya hay una sesión activa o conectando', 'warning');
            return;
        }
        
        try {
            this.isConnecting = true;
            this.updateUI();
            this.log('🚀 Iniciando sesión con OpenAI Realtime API...', 'info');
            
            // 1. Obtener ephemeral key del servidor local
            const ephemeralKey = await this.getEphemeralKey();
            
            // 2. Crear peer connection
            this.peerConnection = new RTCPeerConnection();
            
            // 3. Configurar audio para reproducir respuestas del modelo
            this.setupAudioPlayback();
            
            // 4. Configurar captura de micrófono
            await this.setupMicrophoneInput();
            
            // 5. Configurar data channel para eventos
            this.setupDataChannel();
            
            // 6. Configurar event listeners de WebRTC
            this.setupWebRTCEventListeners();
            
            // 7. Crear offer y conectar a OpenAI
            await this.connectToOpenAI(ephemeralKey);
            
            this.log('✅ Sesión iniciada correctamente', 'success');
            
        } catch (error) {
            this.log(`❌ Error iniciando sesión: ${error.message}`, 'error');
            console.error('Error detallado:', error);
            this.stopSession();
        } finally {
            this.isConnecting = false;
            this.updateUI();
        }
    }
    
    /**
     * 🛑 Detiene la sesión actual
     */
    stopSession() {
        this.log('🛑 Deteniendo sesión...', 'info');
        
        try {
            // Cerrar data channel
            if (this.dataChannel) {
                this.dataChannel.close();
                this.dataChannel = null;
            }
            
            // Detener tracks de audio
            if (this.peerConnection) {
                this.peerConnection.getSenders().forEach(sender => {
                    if (sender.track) {
                        sender.track.stop();
                    }
                });
                
                // Cerrar peer connection
                this.peerConnection.close();
                this.peerConnection = null;
            }
            
            // Limpiar audio element
            if (this.audioElement) {
                this.audioElement.pause();
                this.audioElement.srcObject = null;
                this.audioElement = null;
            }
            
            this.isSessionActive = false;
            this.updateUI();
            this.log('✅ Sesión detenida', 'info');
            
        } catch (error) {
            this.log(`❌ Error deteniendo sesión: ${error.message}`, 'error');
        }
    }
    
    /**
     * 🔑 Obtiene ephemeral key del servidor local
     */
    async getEphemeralKey() {
        this.log('🔑 Obteniendo ephemeral key del servidor...', 'info');
        
        try {
            const response = await fetch(this.config.tokenUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (!data.client_secret || !data.client_secret.value) {
                throw new Error('Ephemeral key no encontrada en la respuesta');
            }
            
            this.log('✅ Ephemeral key obtenida correctamente', 'success');
            return data.client_secret.value;
            
        } catch (error) {
            throw new Error(`Error obteniendo ephemeral key: ${error.message}`);
        }
    }
    
    /**
     * 🔊 Configura la reproducción de audio desde OpenAI
     */
    setupAudioPlayback() {
        this.audioElement = document.createElement("audio");
        this.audioElement.autoplay = true;
        
        // Cuando llega un track de audio desde OpenAI, reproducirlo
        this.peerConnection.ontrack = (event) => {
            this.log('🎵 Audio track recibido desde OpenAI', 'info');
            this.audioElement.srcObject = event.streams[0];
        };
    }
    
    /**
     * 🎤 Configura la captura del micrófono
     */
    async setupMicrophoneInput() {
        this.log('🎤 Configurando captura de micrófono...', 'info');
        
        const constraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: parseInt(this.elements.sampleRate.value),
                channelCount: 1
            }
        };
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Agregar track de audio al peer connection
            const audioTrack = stream.getAudioTracks()[0];
            this.peerConnection.addTrack(audioTrack);
            
            this.log('✅ Micrófono configurado correctamente', 'success');
            
        } catch (error) {
            throw new Error(`Error configurando micrófono: ${error.message}`);
        }
    }
    
    /**
     * 📡 Configura el data channel para intercambio de eventos
     */
    setupDataChannel() {
        // Crear data channel para eventos OpenAI
        this.dataChannel = this.peerConnection.createDataChannel("oai-events");
        
        this.dataChannel.onopen = () => {
            this.log('📡 Data channel abierto', 'success');
            this.isSessionActive = true;
            this.updateUI();
            
            // Enviar evento inicial de configuración
            this.sendClientEvent({
                type: "session.update",
                session: {
                    instructions: "Eres un asistente útil. Responde de manera conversacional y natural en español.",
                    voice: "verse",
                    input_audio_format: "pcm16",
                    output_audio_format: "pcm16",
                    input_audio_transcription: {
                        model: "whisper-1"
                    }
                }
            });
        };
        
        this.dataChannel.onclose = () => {
            this.log('📡 Data channel cerrado', 'warning');
            this.isSessionActive = false;
            this.updateUI();
        };
        
        this.dataChannel.onerror = (error) => {
            this.log(`❌ Error en data channel: ${error}`, 'error');
        };
        
        this.dataChannel.onmessage = (event) => {
            try {
                const serverEvent = JSON.parse(event.data);
                this.handleServerEvent(serverEvent);
            } catch (error) {
                this.log(`❌ Error procesando evento del servidor: ${error.message}`, 'error');
            }
        };
    }
    
    /**
     * 🔗 Configura los event listeners de WebRTC
     */
    setupWebRTCEventListeners() {
        this.peerConnection.onconnectionstatechange = () => {
            const state = this.peerConnection.connectionState;
            this.elements.connectionState.textContent = state;
            this.log(`🔗 Estado de conexión: ${state}`, 'info');
            
            if (state === 'failed' || state === 'disconnected') {
                this.log('❌ Conexión perdida, deteniendo sesión', 'error');
                this.stopSession();
            }
        };
        
        this.peerConnection.onicegatheringstatechange = () => {
            this.log(`🧊 ICE gathering state: ${this.peerConnection.iceGatheringState}`, 'debug');
        };
        
        this.peerConnection.onsignalingstatechange = () => {
            this.log(`📡 Signaling state: ${this.peerConnection.signalingState}`, 'debug');
        };
    }
    
    /**
     * 🌐 Conecta a OpenAI usando WebRTC
     */
    async connectToOpenAI(ephemeralKey) {
        this.log('🌐 Conectando a OpenAI Realtime API...', 'info');
        
        try {
            // Crear offer
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            // Enviar SDP a OpenAI
            const url = `${this.config.openai.baseUrl}?model=${this.config.openai.model}`;
            
            const response = await fetch(url, {
                method: "POST",
                body: offer.sdp,
                headers: {
                    Authorization: `Bearer ${ephemeralKey}`,
                    "Content-Type": "application/sdp",
                },
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Configurar answer
            const answerSdp = await response.text();
            const answer = {
                type: "answer",
                sdp: answerSdp,
            };
            
            await this.peerConnection.setRemoteDescription(answer);
            
            this.log('✅ Conectado a OpenAI Realtime API', 'success');
            
        } catch (error) {
            throw new Error(`Error conectando a OpenAI: ${error.message}`);
        }
    }
    
    /**
     * 📤 Envía un evento al modelo de OpenAI
     */
    sendClientEvent(event) {
        if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
            this.log('⚠️ Data channel no disponible para enviar eventos', 'warning');
            return;
        }
        
        try {
            // Agregar ID único y timestamp
            event.event_id = event.event_id || this.generateEventId();
            
            // Enviar evento
            this.dataChannel.send(JSON.stringify(event));
            
            // Agregar timestamp para el log
            event.timestamp = new Date().toLocaleTimeString();
            this.events.unshift(event);
            
            this.log(`📤 Evento enviado: ${event.type}`, 'debug');
            
        } catch (error) {
            this.log(`❌ Error enviando evento: ${error.message}`, 'error');
        }
    }
    
    /**
     * 📥 Maneja eventos recibidos del servidor OpenAI
     */
    handleServerEvent(event) {
        // Agregar timestamp
        event.timestamp = event.timestamp || new Date().toLocaleTimeString();
        this.events.unshift(event);
        
        this.log(`📥 Evento recibido: ${event.type}`, 'debug');
        
        // Manejar eventos específicos
        switch (event.type) {
            case 'session.created':
                this.log('✅ Sesión creada en OpenAI', 'success');
                break;
                
            case 'session.updated':
                this.log('🔄 Sesión actualizada', 'info');
                break;
                
            case 'input_audio_buffer.speech_started':
                this.log('🗣️ Inicio de habla detectado', 'info');
                this.elements.startBtn.classList.add('recording');
                const startBtnSpan = this.elements.startBtn.querySelector('span');
                if (startBtnSpan) startBtnSpan.textContent = 'Grabando...';
                break;
                
            case 'input_audio_buffer.speech_stopped':
                this.log('🤐 Fin de habla detectado', 'info');
                this.elements.startBtn.classList.remove('recording');
                const stopBtnSpan = this.elements.startBtn.querySelector('span');
                if (stopBtnSpan) stopBtnSpan.textContent = 'Hablar';
                this.showTypingIndicator();
                break;
                
            case 'conversation.item.created':
                this.log('💬 Nuevo ítem de conversación creado', 'info');
                // Si es un mensaje del usuario con transcripción
                if (event.item && event.item.role === 'user' && event.item.content) {
                    const transcript = event.item.content.find(c => c.type === 'input_text' || c.transcript);
                    if (transcript) {
                        const text = transcript.text || transcript.transcript;
                        if (text) {
                            this.addMessage(text, true);
                        }
                    }
                }
                break;
                
            case 'response.created':
                this.log('🔄 Generando respuesta...', 'info');
                this.showTypingIndicator();
                break;
                
            case 'response.audio.delta':
                // Audio streaming en tiempo real
                this.log('🎵 Audio delta recibido', 'debug');
                break;
                
            case 'response.audio.done':
                this.log('🎵 Audio completo recibido', 'info');
                break;
                
            case 'response.text.delta':
                // Texto streaming - agregar al chat
                if (event.delta) {
                    this.handleTextDelta(event.delta);
                }
                break;
                
            case 'response.text.done':
                this.log('� Texto completo recibido', 'info');
                this.hideTypingIndicator();
                break;
                
            case 'response.done':
                this.log('✅ Respuesta completada', 'success');
                this.hideTypingIndicator();
                break;
                
            case 'error':
                this.log(`❌ Error del servidor: ${event.error?.message || 'Error desconocido'}`, 'error');
                this.hideTypingIndicator();
                break;
                
            default:
                this.log(`📝 Evento: ${event.type}`, 'debug');
        }
    }
    
    /**
     * 📝 Maneja deltas de texto streaming
     */
    handleTextDelta(delta) {
        this.hideTypingIndicator();
        
        // Buscar el último mensaje del asistente o crear uno nuevo
        const messages = this.elements.chatMessages.querySelectorAll('.message.assistant:not(.typing-message)');
        let lastAssistantMessage = messages[messages.length - 1];
        
        if (!lastAssistantMessage) {
            // Crear nuevo mensaje
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            bubbleDiv.textContent = delta;
            
            messageDiv.appendChild(bubbleDiv);
            this.elements.chatMessages.appendChild(messageDiv);
        } else {
            // Agregar al mensaje existente
            const bubble = lastAssistantMessage.querySelector('.message-bubble');
            if (bubble) {
                bubble.textContent += delta;
            }
        }
        
        // Scroll al final
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * 💬 Maneja el input de texto del usuario
     */
    handleTextInput() {
        const message = this.elements.textInput.value.trim();
        if (message) {
            this.sendTextMessage(message);
            this.elements.textInput.value = '';
        }
    }
    
    /**
     * 💬 Envía un mensaje de texto al modelo
     */
    sendTextMessage(message) {
        if (!message.trim()) return;
        
        // Mostrar mensaje del usuario en el chat
        this.addMessage(message, true);
        
        // Crear ítem de conversación
        this.sendClientEvent({
            type: "conversation.item.create",
            item: {
                type: "message",
                role: "user",
                content: [{
                    type: "input_text",
                    text: message
                }]
            }
        });
        
        // Solicitar respuesta
        this.sendClientEvent({
            type: "response.create"
        });
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        this.log(`💬 Mensaje enviado: "${message}"`, 'info');
    }
    
    /**
     * 🆔 Genera un ID único para eventos
     */
    generateEventId() {
        return 'event_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * 🎨 Actualiza la interfaz de usuario
     */
    updateUI() {
        // Estado de conexión
        const isConnected = this.isSessionActive;
        this.elements.connectionStatus.className = `status-dot ${
            isConnected ? 'connected' : 'disconnected'
        }`;
        
        this.elements.statusText.textContent = isConnected ? 'Conectado' : 'Desconectado';
        
        // Botones principales
        this.elements.startBtn.disabled = this.isSessionActive || this.isConnecting;
        this.elements.stopBtn.disabled = !this.isSessionActive && !this.isConnecting;
        
        // Input de texto
        this.elements.textInput.disabled = !this.isSessionActive;
        this.elements.sendTextBtn.disabled = !this.isSessionActive;
        
        // Configuración
        if (this.elements.sampleRate) {
            this.elements.sampleRate.disabled = this.isSessionActive || this.isConnecting;
        }
        if (this.elements.bitrate) {
            this.elements.bitrate.disabled = this.isSessionActive || this.isConnecting;
        }
        
        // Texto y estado de botones de voz
        const startBtnSpan = this.elements.startBtn.querySelector('span');
        if (this.isConnecting) {
            if (startBtnSpan) startBtnSpan.textContent = 'Conectando...';
            this.elements.startBtn.classList.remove('recording');
        } else if (this.isSessionActive) {
            if (startBtnSpan) startBtnSpan.textContent = 'Hablar';
            this.elements.startBtn.classList.remove('recording');
        } else {
            if (startBtnSpan) startBtnSpan.textContent = 'Hablar';
            this.elements.startBtn.classList.remove('recording');
        }
        
        const stopBtnSpan = this.elements.stopBtn.querySelector('span');
        if (stopBtnSpan) stopBtnSpan.textContent = 'Detener';
    }
    
    /**
     * 📝 Sistema de logging mejorado con colores y mejor formato
     */
    log(message, type = 'info') {
        // Solo crear elementos de log si el contenedor existe (elementos ocultos)
        if (!this.elements.logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        
        // Iconos y colores para diferentes tipos de log
        const logTypes = {
            'info': { icon: '💡', label: 'INFO', color: '#3b82f6' },
            'success': { icon: '✅', label: 'SUCCESS', color: '#10b981' },
            'warning': { icon: '⚠️', label: 'WARNING', color: '#f59e0b' },
            'error': { icon: '❌', label: 'ERROR', color: '#ef4444' },
            'debug': { icon: '🔍', label: 'DEBUG', color: '#8b5cf6' }
        };
        
        const logType = logTypes[type] || logTypes['info'];
        
        logEntry.innerHTML = `
            <div class="log-entry-content">
                <div class="log-header">
                    <span class="log-icon">${logType.icon}</span>
                    <span class="log-type" style="color: ${logType.color};">${logType.label}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-message">${escapeHTML(message)}</div>
            </div>
        `;
        
        this.elements.logContainer.appendChild(logEntry);
        this.elements.logContainer.scrollTop = this.elements.logContainer.scrollHeight;
        
        // Limitar entradas del log
        const entries = this.elements.logContainer.children;
        if (entries.length > 100) {
            this.elements.logContainer.removeChild(entries[0]);
        }
        
        // También log a consola con colores
        const consoleColors = {
            'info': 'color: #3b82f6; font-weight: bold;',
            'success': 'color: #10b981; font-weight: bold;',
            'warning': 'color: #f59e0b; font-weight: bold;',
            'error': 'color: #ef4444; font-weight: bold;',
            'debug': 'color: #8b5cf6; font-weight: bold;'
        };
        
        console.log(
            `%c[${logType.label}] %c${message}`,
            consoleColors[type] || consoleColors['info'],
            'color: inherit; font-weight: normal;'
        );
    }
}

// 🚀 Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeClient = new OpenAIRealtimeClient();
    
    // Exponer función para enviar mensajes desde la consola del navegador
    window.sendMessage = (message) => {
        if (window.realtimeClient.isSessionActive) {
            window.realtimeClient.sendTextMessage(message);
        } else {
            console.log('❌ Sesión no activa. Inicia una sesión primero.');
        }
    };
    
    console.log('🎤 Cliente OpenAI Realtime inicializado');
    console.log('💡 Usa sendMessage("tu mensaje") para enviar mensajes de texto');
});
