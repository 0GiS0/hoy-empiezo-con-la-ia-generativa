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
                const port = 8000; // Puerto del servidor Python
                return `${protocol}${host}:${port}/token`;
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
            sendTextBtn: document.getElementById('sendTextBtn')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateUI();
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
                break;
                
            case 'input_audio_buffer.speech_stopped':
                this.log('🤐 Fin de habla detectado', 'info');
                break;
                
            case 'conversation.item.created':
                this.log('💬 Nuevo ítem de conversación creado', 'info');
                break;
                
            case 'response.audio.delta':
                // Audio streaming en tiempo real
                this.log('🎵 Audio delta recibido', 'debug');
                break;
                
            case 'response.audio.done':
                this.log('🎵 Audio de respuesta completado', 'info');
                break;
                
            case 'response.text.delta':
                this.log(`💭 Texto: ${event.delta || ''}`, 'info');
                break;
                
            case 'error':
                this.log(`❌ Error del servidor: ${event.error?.message || 'Error desconocido'}`, 'error');
                break;
                
            default:
                this.log(`📝 Evento: ${event.type}`, 'debug');
        }
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
        this.elements.connectionStatus.className = `status-indicator ${
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
        this.elements.sampleRate.disabled = this.isSessionActive || this.isConnecting;
        this.elements.bitrate.disabled = this.isSessionActive || this.isConnecting;
        
        // Texto de botones
        if (this.isConnecting) {
            this.elements.startBtn.textContent = 'Conectando...';
        } else {
            this.elements.startBtn.textContent = 'Iniciar Sesión';
        }
    }
    
    /**
     * 📝 Sistema de logging
     */
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        
        // Iconos para diferentes tipos de log
        const icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'debug': '🔍'
        };
        
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="icon">${icons[type] || 'ℹ️'}</span>
            <span class="message">${escapeHTML(message)}</span>
        `;
        
        this.elements.logContainer.appendChild(logEntry);
        this.elements.logContainer.scrollTop = this.elements.logContainer.scrollHeight;
        
        // Limitar entradas del log
        const entries = this.elements.logContainer.children;
        if (entries.length > 100) {
            this.elements.logContainer.removeChild(entries[0]);
        }
        
        // También log a consola
        console.log(`[${type.toUpperCase()}] ${message}`);
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
