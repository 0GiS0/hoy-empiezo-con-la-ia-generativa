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

/**
 * 🎯 Clase principal que maneja la comunicación con OpenAI Realtime API
 * Esta clase utiliza WebRTC para establecer una conexión bidireccional en tiempo real
 * permitiendo envío de audio del micrófono y recepción de respuestas de voz del modelo
 */
class OpenAIRealtimeClient {
    constructor() {
        // 🏗️ Estado de la aplicación - Variables que controlan el flujo de la app
        this.isSessionActive = false;    // 🔴 ¿Hay una sesión activa con OpenAI?
        this.isConnecting = false;       // 🟡 ¿Estamos en proceso de conectar?
        this.events = [];               // 📋 Historial de eventos enviados/recibidos
        this.dataChannel = null;        // 📡 Canal de datos WebRTC para eventos JSON
        this.peerConnection = null;     // 🔗 Conexión WebRTC principal
        this.audioElement = null;       // 🔊 Elemento HTML para reproducir audio de OpenAI
        
        // ⏱️ Sistema de medición de latencia
        this.responseTimers = {
            speechStart: null,          // 🗣️ Timestamp cuando empieza a hablar
            speechEnd: null,            // 🤐 Timestamp cuando termina de hablar
            responseStart: null,        // 🔄 Timestamp cuando empieza la respuesta
            responseEnd: null,          // ✅ Timestamp cuando termina la respuesta
            textStart: null,            // 📝 Timestamp cuando empieza respuesta de texto
            textEnd: null,              // ✅ Timestamp cuando termina respuesta de texto
            audioStart: null,           // 🎵 Timestamp cuando empieza respuesta de audio
            audioEnd: null,             // 🎵 Timestamp cuando termina respuesta de audio
        };
        
        // ⚙️ Configuración - URLs y parámetros del cliente
        this.config = {
            // 🌐 URL del servidor local para obtener ephemeral keys
            // Los ephemeral keys son tokens temporales que permiten conectar a OpenAI
            // sin exponer tu API key real en el frontend
            get tokenUrl() {
                const protocol = window.location.protocol === 'https:' ? 'https://' : 'http://';
                const host = window.location.hostname;
                const port = window.location.port || 8000; // Usar el puerto actual o 8000 por defecto
                return `${protocol}${host}:${port}/api/token`;
            },
            // 🤖 OpenAI Realtime API configuration
            openai: {
                baseUrl: "https://api.openai.com/v1/realtime",         // 🔗 Endpoint oficial de OpenAI
                model: "gpt-4o-realtime-preview-2024-12-17"            // 🧠 Modelo específico para tiempo real
            }
        };
        
        // 🎯 Elementos del DOM - Referencias a todos los elementos HTML que necesitamos
        this.elements = {
            startBtn: document.getElementById('startBtn'),              // 🎤 Botón para iniciar sesión de voz
            stopBtn: document.getElementById('stopBtn'),                // 🛑 Botón para detener sesión
            connectionStatus: document.getElementById('connectionStatus'), // 🔴🟢 Indicador visual de conexión
            statusText: document.getElementById('statusText'),          // 📝 Texto del estado actual
            volumeFill: document.getElementById('volumeFill'),          // 📊 Indicador visual de volumen
            volumeText: document.getElementById('volumeText'),          // 📊 Texto del nivel de volumen
            connectionState: document.getElementById('connectionState'), // 🔗 Estado detallado de WebRTC
            bytesSent: document.getElementById('bytesSent'),            // 📈 Contador de bytes enviados
            packetsSent: document.getElementById('packetsSent'),        // 📦 Contador de paquetes enviados
            latency: document.getElementById('latency'),                // ⏱️ Medidor de latencia
            responseTime: document.getElementById('responseTime'),  // ⏱️ Tiempo de respuesta
            logContainer: document.getElementById('logContainer'),      // 📋 Contenedor de logs
            sampleRate: document.getElementById('sampleRate'),          // 🎵 Selector de frecuencia de muestreo
            bitrate: document.getElementById('bitrate'),                // 💾 Selector de bitrate
            textInput: document.getElementById('textInput'),            // ⌨️ Input para mensajes de texto
            sendTextBtn: document.getElementById('sendTextBtn'),        // 📤 Botón enviar texto
            chatMessages: document.getElementById('chatMessages'),      // 💬 Contenedor de mensajes del chat
            logPanel: document.getElementById('logPanel'),              // 📊 Panel de logs técnicos
            logToggleBtn: document.getElementById('logToggleBtn'),      // 👁️ Botón mostrar/ocultar logs
            clearLogsBtn: document.getElementById('clearLogsBtn')       // 🗑️ Botón limpiar logs
        };
        
        // 🚀 Inicializar la aplicación
        this.init();
    }
    
    /**
     * 🔧 Método de inicialización principal
     * Configura todos los componentes necesarios para que la app funcione
     */
    init() {
        this.setupEventListeners();    // 👂 Configurar escuchadores de eventos
        this.setupLogPanel();          // 📋 Configurar panel de logs
        this.updateUI();               // 🎨 Actualizar interfaz inicial
        this.clearWelcomeMessage();    // 🧹 Limpiar mensaje de bienvenida si existe
        this.log('🎤 Cliente OpenAI Realtime inicializado', 'info');
        this.log('💡 Basado en el ejemplo oficial de OpenAI con WebRTC', 'info');
    }
    
    /**
     * 👂 Configurar todos los event listeners de la interfaz
     * Aquí conectamos los botones y elementos con sus respectivas funciones
     */
    setupEventListeners() {
        // 🎤 Botones principales de control de sesión
        this.elements.startBtn.addEventListener('click', () => this.startSession());
        this.elements.stopBtn.addEventListener('click', () => this.stopSession());
        
        // ⌨️ Funcionalidad de input de texto - dos formas de enviar mensaje
        this.elements.sendTextBtn.addEventListener('click', () => this.handleTextInput());
        this.elements.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {  // 📤 Enviar con Enter
                this.handleTextInput();
            }
        });
        
        // ⚙️ Detectar cambios en la configuración de audio
        // Si cambia el sample rate durante una sesión activa, necesitamos reiniciar
        this.elements.sampleRate.addEventListener('change', () => {
            if (this.isSessionActive) {
                this.log('⚠️ Configuración cambiada, reiniciando sesión...', 'warning');
                this.stopSession();
                setTimeout(() => this.startSession(), 1000); // 🔄 Reiniciar después de 1 segundo
            }
        });
    }
    
    /**
     * 📋 Configurar panel de logs técnicos
     * Los logs ayudan a debuggear y entender qué está pasando internamente
     */
    setupLogPanel() {
        // 👁️ Toggle panel de logs - mostrar/ocultar
        this.elements.logToggleBtn.addEventListener('click', () => {
            const isHidden = this.elements.logPanel.classList.contains('hidden');
            if (isHidden) {
                this.elements.logPanel.classList.remove('hidden');        // 👀 Mostrar logs
                this.elements.logToggleBtn.classList.add('active');
                this.elements.logToggleBtn.title = 'Ocultar logs';
            } else {
                this.elements.logPanel.classList.add('hidden');           // 🙈 Ocultar logs
                this.elements.logToggleBtn.classList.remove('active');
                this.elements.logToggleBtn.title = 'Mostrar logs';
            }
        });
        
        // 🗑️ Limpiar todos los logs
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
     * 💬 Agregar un mensaje al chat visual
     * @param {string} content - El texto del mensaje
     * @param {boolean} isUser - true si es mensaje del usuario, false si es del asistente
     */
    addMessage(content, isUser = false) {
        this.clearWelcomeMessage(); // 🧹 Quitar mensaje de bienvenida al empezar a chatear
        
        // 🏗️ Crear estructura HTML del mensaje
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;
        
        messageDiv.appendChild(bubbleDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        
        // 📜 Scroll automático al último mensaje
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * ⏳ Mostrar indicador de "escribiendo..." mientras el asistente piensa
     * Proporciona feedback visual de que la IA está procesando la respuesta
     */
    showTypingIndicator() {
        this.hideTypingIndicator(); // 🧹 Eliminar indicador previo por si acaso
        
        // 🎭 Crear animación de puntos que se mueven
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-message';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>    <!-- 🔵 Punto 1 -->
                <div class="typing-dot"></div>    <!-- 🔵 Punto 2 -->
                <div class="typing-dot"></div>    <!-- 🔵 Punto 3 -->
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
     * 📝 Mostrar indicador de transcripción en tiempo real
     */
    showTranscriptionIndicator() {
        this.hideTranscriptionIndicator(); // 🧹 Eliminar indicador previo

        // 🎭 Crear elemento para mostrar transcripción en tiempo real
        const transcriptionDiv = document.createElement('div');
        transcriptionDiv.className = 'message user transcription-message';
        transcriptionDiv.innerHTML = `
            <div class="transcription-bubble">
                <div class="transcription-header">
                    <span class="transcription-icon">🎤</span>
                    <span class="transcription-label">Transcribiendo...</span>
                    <div class="transcription-wave">
                        <div class="wave-dot"></div>
                        <div class="wave-dot"></div>
                        <div class="wave-dot"></div>
                    </div>
                </div>
                <div class="transcription-text" id="live-transcription">
                    Escuchando...
                </div>
            </div>
        `;

        this.elements.chatMessages.appendChild(transcriptionDiv);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    /**
     * 🚫 Ocultar indicador de transcripción
     */
    hideTranscriptionIndicator() {
        const transcriptionMessage = this.elements.chatMessages.querySelector('.transcription-message');
        if (transcriptionMessage) {
            transcriptionMessage.remove();
        }
    }

    /**
     * 📝 Actualizar texto de transcripción en tiempo real
     * @param {string} text - Texto transcrito
     * @param {boolean} isComplete - Si la transcripción está completa
     */
    updateTranscriptionDisplay(text, isComplete = false) {
        const transcriptionText = document.getElementById('live-transcription');
        if (transcriptionText) {
            transcriptionText.textContent = text;
            
            if (isComplete) {
                // 🎯 Marcar como completada con estilo diferente
                const transcriptionBubble = transcriptionText.closest('.transcription-bubble');
                if (transcriptionBubble) {
                    transcriptionBubble.classList.add('completed');
                    const label = transcriptionBubble.querySelector('.transcription-label');
                    if (label) label.textContent = 'Transcrito';
                }
            }
        }

        // 📜 Scroll automático
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    /**
     * ✅ Finalizar transcripción y convertirla en mensaje definitivo
     * @param {string} finalText - Texto final transcrito
     */
    finalizeTranscription(finalText) {
        // 🧹 Remover indicador de transcripción
        this.hideTranscriptionIndicator();
        
        // 💬 Añadir mensaje final del usuario
        this.addMessage(finalText, true);
    }
    
    /**
     * 🚀 Método principal que inicia una nueva sesión con OpenAI Realtime API
     * Este es el corazón de la aplicación - establece la conexión completa
     */
    async startSession() {
        // 🚫 Prevenir múltiples conexiones simultáneas
        if (this.isConnecting || this.isSessionActive) {
            this.log('⚠️ Ya hay una sesión activa o conectando', 'warning');
            return;
        }
        
        try {
            this.isConnecting = true;
            this.updateUI();
            this.log('🚀 Iniciando sesión con OpenAI Realtime API...', 'info');
            
            // 🔐 1. Obtener ephemeral key del servidor local (token temporal)
            const ephemeralKey = await this.getEphemeralKey();
            
            // 🔗 2. Crear peer connection WebRTC (la conexión principal)
            this.peerConnection = new RTCPeerConnection();
            
            // 🔊 3. Configurar audio para reproducir respuestas del modelo
            this.setupAudioPlayback();
            
            // 🎤 4. Configurar captura de micrófono del usuario
            await this.setupMicrophoneInput();
            
            // 📡 5. Configurar data channel para intercambio de eventos JSON
            this.setupDataChannel();
            
            // 👂 6. Configurar event listeners de WebRTC (monitoreo de conexión)
            this.setupWebRTCEventListeners();
            
            // 🌐 7. Crear offer y conectar a OpenAI (handshake final)
            await this.connectToOpenAI(ephemeralKey);
            
            this.log('✅ Sesión iniciada correctamente', 'success');
            
        } catch (error) {
            this.log(`❌ Error iniciando sesión: ${error.message}`, 'error');
            console.error('Error detallado:', error);
            this.stopSession(); // 🧹 Limpiar en caso de error
        } finally {
            this.isConnecting = false;
            this.updateUI();
        }
    }
    
    /**
     * 🛑 Detiene la sesión actual y limpia todos los recursos
     * Importante hacer cleanup completo para evitar memory leaks
     */
    stopSession() {
        this.log('🛑 Deteniendo sesión...', 'info');
        
        try {
            // 📡 Cerrar data channel (canal de eventos JSON)
            if (this.dataChannel) {
                this.dataChannel.close();
                this.dataChannel = null;
            }
            
            // 🎤 Detener todos los tracks de audio (liberar micrófono)
            if (this.peerConnection) {
                this.peerConnection.getSenders().forEach(sender => {
                    if (sender.track) {
                        sender.track.stop(); // 🔇 Liberar el micrófono
                    }
                });
                
                // 🔗 Cerrar la conexión WebRTC completamente
                this.peerConnection.close();
                this.peerConnection = null;
            }
            
            // 🔊 Limpiar elemento de audio (detener reproducción)
            if (this.audioElement) {
                this.audioElement.pause();
                this.audioElement.srcObject = null; // 🧹 Liberar stream
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
     * Los ephemeral keys son tokens temporales que permiten usar la API
     * sin exponer la API key real en el frontend (más seguro)
     */
    async getEphemeralKey() {
        this.log('🔑 Obteniendo ephemeral key del servidor...', 'info');
        
        try {
            // 🌐 Hacer petición POST al servidor local
            const response = await fetch(this.config.tokenUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            // ⚠️ Verificar que la respuesta sea exitosa
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // 🔍 Verificar que el token esté en la respuesta
            if (!data.client_secret || !data.client_secret.value) {
                throw new Error('Ephemeral key no encontrada en la respuesta');
            }
            
            this.log('✅ Ephemeral key obtenida correctamente', 'success');
            return data.client_secret.value; // 🎟️ Retornar el token
            
        } catch (error) {
            throw new Error(`Error obteniendo ephemeral key: ${error.message}`);
        }
    }
    
    /**
     * 🔊 Configura la reproducción de audio desde OpenAI
     * Cuando OpenAI envía respuestas de voz, las reproducimos automáticamente
     */
    setupAudioPlayback() {
        // 🎵 Crear elemento de audio HTML5 para reproducir respuestas
        this.audioElement = document.createElement("audio");
        this.audioElement.autoplay = true; // ▶️ Reproducir automáticamente
        
        // 🎧 Cuando llega un track de audio desde OpenAI, conectarlo al reproductor
        this.peerConnection.ontrack = (event) => {
            this.log('🎵 Audio track recibido desde OpenAI', 'info');
            
            // ⏱️ Marcar primera recepción de audio si no se ha marcado aún
            if (!this.responseTimers.audioStart && this.responseTimers.speechEnd) {
                this.responseTimers.audioStart = Date.now();
                this.log('🎵 Primera recepción de audio detectada', 'info');
                this.calculateAndShowResponseTime(); // Mostrar tiempo parcial
            }
            
            // 🔗 Conectar el stream de audio al elemento HTML
            this.audioElement.srcObject = event.streams[0];
        };
    }
    
    /**
     * 🎤 Configura la captura del micrófono del usuario
     * Solicita permisos y configura el stream de audio con parámetros optimizados
     */
    async setupMicrophoneInput() {
        this.log('🎤 Configurando captura de micrófono...', 'info');
        
        // ⚙️ Configuración de audio optimizada para conversación
        const constraints = {
            audio: {
                echoCancellation: true,    // 🔇 Cancelar eco para evitar feedback
                noiseSuppression: true,    // 🔇 Suprimir ruido de fondo
                autoGainControl: true,     // 📊 Control automático de ganancia
                sampleRate: parseInt(this.elements.sampleRate.value), // 🎵 Frecuencia configurada
                channelCount: 1           // 🔊 Mono (una sola canal)
            }
        };
        
        try {
            // 🎤 Solicitar acceso al micrófono del usuario
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // 🎧 Obtener el track de audio del stream
            const audioTrack = stream.getAudioTracks()[0];
            // 📡 Agregar el track a la conexión WebRTC (enviar a OpenAI)
            this.peerConnection.addTrack(audioTrack);
            
            this.log('✅ Micrófono configurado correctamente', 'success');
            
        } catch (error) {
            throw new Error(`Error configurando micrófono: ${error.message}`);
        }
    }
    
    /**
     * 📡 Configura el data channel para intercambio de eventos JSON
     * Los data channels permiten enviar datos estructurados (eventos) además de audio
     */
    setupDataChannel() {
        // 🚧 Crear canal de datos etiquetado para eventos OpenAI
        this.dataChannel = this.peerConnection.createDataChannel("oai-events");
        
        // ✅ Cuando el canal se abre, configurar la sesión
        this.dataChannel.onopen = () => {
            this.log('📡 Data channel abierto', 'success');
            this.isSessionActive = true;
            this.updateUI();
            
            // 🔧 Enviar configuración inicial a OpenAI
            this.sendClientEvent({
                type: "session.update",
                session: {
                    instructions: "Eres un asistente útil. Responde de manera conversacional y natural en español.", // 🗣️ Personalidad
                    voice: "verse",                        // 🎭 Voz específica
                    input_audio_format: "pcm16",          // 🎵 Formato audio entrada
                    output_audio_format: "pcm16",         // 🎵 Formato audio salida
                    input_audio_transcription: {          // 📝 Transcripción automática
                        model: "whisper-1"
                    }
                }
            });
        };
        
        // ⚠️ Cuando el canal se cierra
        this.dataChannel.onclose = () => {
            this.log('📡 Data channel cerrado', 'warning');
            this.isSessionActive = false;
            this.updateUI();
        };
        
        // ❌ Manejo de errores del canal
        this.dataChannel.onerror = (error) => {
            this.log(`❌ Error en data channel: ${error}`, 'error');
        };
        
        // 📥 Cuando llegan eventos desde OpenAI
        this.dataChannel.onmessage = (event) => {
            try {
                const serverEvent = JSON.parse(event.data); // 🔄 Parsear JSON
                this.handleServerEvent(serverEvent);        // 🎯 Procesar evento
            } catch (error) {
                this.log(`❌ Error procesando evento del servidor: ${error.message}`, 'error');
            }
        };
    }
    
    /**
     * 🔗 Configura los event listeners de WebRTC para monitorear la conexión
     * WebRTC tiene varios estados que nos ayudan a debuggear problemas
     */
    setupWebRTCEventListeners() {
        // 🔄 Monitorear cambios en el estado de la conexión
        this.peerConnection.onconnectionstatechange = () => {
            const state = this.peerConnection.connectionState;
            this.elements.connectionState.textContent = state;
            this.log(`🔗 Estado de conexión: ${state}`, 'info');
            
            // 💔 Si la conexión falla o se desconecta, limpiar todo
            if (state === 'failed' || state === 'disconnected') {
                this.log('❌ Conexión perdida, deteniendo sesión', 'error');
                this.stopSession();
            }
        };
        
        // 🧊 Monitorear el proceso de ICE gathering (recolección de candidatos)
        this.peerConnection.onicegatheringstatechange = () => {
            this.log(`🧊 ICE gathering state: ${this.peerConnection.iceGatheringState}`, 'debug');
        };
        
        // 📡 Monitorear cambios en el signaling state (negociación WebRTC)
        this.peerConnection.onsignalingstatechange = () => {
            this.log(`📡 Signaling state: ${this.peerConnection.signalingState}`, 'debug');
        };
    }
    
    /**
     * 🌐 Conecta a OpenAI usando WebRTC con el protocolo SDP
     * SDP (Session Description Protocol) describe los parámetros de la sesión multimedia
     */
    async connectToOpenAI(ephemeralKey) {
        this.log('🌐 Conectando a OpenAI Realtime API...', 'info');
        
        try {
            // 📋 1. Crear "offer" - describe qué podemos enviar/recibir
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            // 🌐 2. Construir URL con el modelo específico
            const url = `${this.config.openai.baseUrl}?model=${this.config.openai.model}`;
            
            // 📤 3. Enviar SDP offer a OpenAI con autenticación
            const response = await fetch(url, {
                method: "POST",
                body: offer.sdp,                                // 📋 Descripción de sesión
                headers: {
                    Authorization: `Bearer ${ephemeralKey}`,    // 🔑 Token de autenticación
                    "Content-Type": "application/sdp",         // 📄 Tipo de contenido SDP
                },
            });
            
            // ⚠️ Verificar respuesta exitosa
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // 📥 4. Configurar "answer" - respuesta de OpenAI con sus capacidades
            const answerSdp = await response.text();
            const answer = {
                type: "answer",
                sdp: answerSdp,
            };
            
            // 🔗 5. Establecer la descripción remota (completar handshake)
            await this.peerConnection.setRemoteDescription(answer);
            
            this.log('✅ Conectado a OpenAI Realtime API', 'success');
            
        } catch (error) {
            throw new Error(`Error conectando a OpenAI: ${error.message}`);
        }
    }
    
    /**
     * 📤 Envía un evento JSON al modelo de OpenAI a través del data channel
     * Los eventos permiten controlar la conversación y enviar comandos específicos
     */
    sendClientEvent(event) {
        // 🚫 Verificar que el canal esté disponible antes de enviar
        if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
            this.log('⚠️ Data channel no disponible para enviar eventos', 'warning');
            return;
        }
        
        try {
            // 🆔 Agregar ID único y timestamp para tracking
            event.event_id = event.event_id || this.generateEventId();
            
            // 📤 Convertir a JSON y enviar por el canal
            this.dataChannel.send(JSON.stringify(event));
            
            // 📝 Guardar en historial para debugging
            event.timestamp = new Date().toLocaleTimeString();
            this.events.unshift(event); // Agregar al inicio del array
            
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
                // 🗣️ Usuario empezó a hablar - indicador visual
                this.responseTimers.speechStart = Date.now(); // ⏱️ Marcar inicio
                this.log('🗣️ Inicio de habla detectado', 'info');
                this.elements.startBtn.classList.add('recording');
                const startBtnSpan = this.elements.startBtn.querySelector('span');
                if (startBtnSpan) startBtnSpan.textContent = 'Grabando...';
                
                // 🧹 Limpiar indicador de tiempo de respuesta para nueva medición
                this.elements.responseTime.textContent = 'Midiendo...';
                this.elements.responseTime.className = 'metric-value processing';
                
                // 📝 Mostrar indicador de transcripción en tiempo real
                this.showTranscriptionIndicator();
                break;
                
            case 'input_audio_buffer.speech_stopped':
                // 🤐 Usuario dejó de hablar - procesar audio
                this.responseTimers.speechEnd = Date.now(); // ⏱️ Marcar fin de habla
                this.log('🤐 Fin de habla detectado', 'info');
                this.elements.startBtn.classList.remove('recording');
                const stopBtnSpan = this.elements.startBtn.querySelector('span');
                if (stopBtnSpan) stopBtnSpan.textContent = 'Hablar';
                
                // 📊 Actualizar indicador de tiempo de respuesta
                this.elements.responseTime.textContent = 'Procesando...';
                this.elements.responseTime.className = 'metric-value processing';
                
                this.showTypingIndicator(); // ⏳ Mostrar que está procesando
                break;

            case 'input_audio_buffer.committed':
                this.log('📝 Audio buffer confirmado', 'debug');
                // 🧹 Ocultar indicador de transcripción cuando se confirma el audio
                this.hideTranscriptionIndicator();
                break;

            case 'input_audio_buffer.transcription_completed':
                // 📝 Transcripción completa del audio del usuario
                if (event.transcript) {
                    this.log(`📝 Transcripción completa: "${event.transcript}"`, 'info');
                    this.updateTranscriptionDisplay(event.transcript, true); // true = completada
                }
                break;

            case 'input_audio_buffer.transcription_failed':
                this.log('❌ Error en transcripción', 'error');
                this.hideTranscriptionIndicator();
                break;
                
            case 'conversation.item.created':
                this.log('💬 Nuevo ítem de conversación creado', 'info');
                // 📝 Si es un mensaje del usuario con transcripción, mostrarlo
                if (event.item && event.item.role === 'user' && event.item.content) {
                    const transcript = event.item.content.find(c => c.type === 'input_audio_transcription' || c.type === 'input_text');
                    if (transcript) {
                        const text = transcript.transcript || transcript.text;
                        if (text) {
                            this.log(`👤 Transcripción del usuario: "${text}"`, 'info');
                            // � Actualizar el mensaje de transcripción con el texto final
                            this.finalizeTranscription(text);
                        }
                    }
                }
                break;
                
            case 'response.created':
                this.responseTimers.responseStart = Date.now(); // ⏱️ Marcar inicio de respuesta
                this.log('🔄 Generando respuesta...', 'info');
                this.showTypingIndicator();
                break;
                
            case 'response.output_item.added':
                // 📋 Se agregó un nuevo item de respuesta (puede ser texto o audio)
                this.log('📋 Item de respuesta agregado', 'info');
                
                // ⏱️ Marcar primer output si no hemos empezado aún
                if (!this.responseTimers.textStart && !this.responseTimers.audioStart && this.responseTimers.speechEnd) {
                    const now = Date.now();
                    if (event.item && event.item.type === 'audio') {
                        this.responseTimers.audioStart = now;
                        this.log('🎵 Primera respuesta de audio iniciada', 'info');
                    } else {
                        this.responseTimers.textStart = now;
                        this.log('📝 Primera respuesta de texto iniciada', 'info');
                    }
                    this.calculateAndShowResponseTime(); // Mostrar tiempo parcial
                }
                break;
                
            case 'response.audio.delta':
                // Audio streaming en tiempo real
                // ⏱️ Marcar inicio de audio si es el primer delta
                if (!this.responseTimers.audioStart) {
                    this.responseTimers.audioStart = Date.now();
                    this.log('🎵 Primera respuesta de audio recibida', 'info');
                }
                this.log('🎵 Audio delta recibido', 'debug');
                break;
                
            case 'response.audio.done':
                this.responseTimers.audioEnd = Date.now(); // ⏱️ Marcar fin de audio
                this.log('🎵 Audio completo recibido', 'info');
                this.calculateAndShowResponseTime(); // 📊 Calcular tiempos para audio
                break;
                
            case 'response.text.delta':
                // Texto streaming - agregar al chat
                if (event.delta) {
                    // ⏱️ Marcar inicio de texto si es el primer delta
                    if (!this.responseTimers.textStart) {
                        this.responseTimers.textStart = Date.now();
                    }
                    this.handleTextDelta(event.delta);
                }
                break;
                
            case 'response.text.done':
                this.responseTimers.textEnd = Date.now(); // ⏱️ Marcar fin de texto
                this.log('📝 Texto completo recibido', 'info');
                this.calculateAndShowResponseTime(); // 📊 Calcular tiempos
                this.hideTypingIndicator();
                break;
                
            case 'response.done':
                this.responseTimers.responseEnd = Date.now(); // ⏱️ Marcar fin de respuesta
                this.log('✅ Respuesta completada', 'success');
                
                // 📊 Si no tenemos un tiempo de fin específico de texto/audio, usar este
                if (!this.responseTimers.textEnd && !this.responseTimers.audioEnd) {
                    this.responseTimers.textEnd = this.responseTimers.responseEnd;
                }
                
                this.calculateAndShowResponseTime(); // 📊 Calcular tiempos finales
                this.hideTypingIndicator();
                break;
                
            case 'error':
                this.log(`❌ Error del servidor: ${event.error?.message || 'Error desconocido'}`, 'error');
                this.hideTypingIndicator();
                break;
                
            default:
                this.log(`📝 Evento no manejado: ${event.type}`, 'debug');
                
                // 🔍 Para eventos de respuesta que no estamos manejando específicamente
                if (event.type.startsWith('response.') && this.responseTimers.speechEnd) {
                    // ⏱️ Si es el primer evento de respuesta, marcarlo
                    if (!this.responseTimers.textStart && !this.responseTimers.audioStart) {
                        const now = Date.now();
                        this.responseTimers.textStart = now;
                        this.log(`🎯 Primer evento de respuesta detectado: ${event.type}`, 'info');
                        this.calculateAndShowResponseTime(); // Mostrar tiempo parcial
                    }
                }
        }
    }
    
    /**
     * 📝 Maneja deltas de texto streaming para mostrar respuestas en tiempo real
     * Los deltas son fragmentos de texto que llegan gradualmente, creando efecto de escritura
     */
    handleTextDelta(delta) {
        this.hideTypingIndicator(); // 🚫 Quitar puntos de "escribiendo"
        
        // 🔍 Buscar el último mensaje del asistente o crear uno nuevo
        const messages = this.elements.chatMessages.querySelectorAll('.message.assistant:not(.typing-message)');
        let lastAssistantMessage = messages[messages.length - 1];
        
        if (!lastAssistantMessage) {
            // 🆕 Crear nuevo mensaje si no existe
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            
            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'message-bubble';
            bubbleDiv.textContent = delta; // 📝 Primer fragmento de texto
            
            messageDiv.appendChild(bubbleDiv);
            this.elements.chatMessages.appendChild(messageDiv);
        } else {
            // ➕ Agregar al mensaje existente (efecto streaming)
            const bubble = lastAssistantMessage.querySelector('.message-bubble');
            if (bubble) {
                bubble.textContent += delta; // 📝 Concatenar nuevo texto
            }
        }
        
        // 📜 Scroll automático al final para seguir el texto
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    /**
     * 💬 Maneja el input de texto del usuario desde la interfaz
     * Procesa el texto escrito y lo prepara para envío
     */
    handleTextInput() {
        const message = this.elements.textInput.value.trim();
        if (message) {
            this.sendTextMessage(message);          // 📤 Enviar mensaje
            this.elements.textInput.value = '';     // 🧹 Limpiar input
        }
    }
    
    /**
     * 💬 Envía un mensaje de texto al modelo usando eventos estructurados
     * Alternativa al audio - permite comunicación por texto
     */
    sendTextMessage(message) {
        if (!message.trim()) return; // 🚫 No enviar mensajes vacíos
        
        // ⏱️ Marcar inicio de interacción para texto
        this.responseTimers.speechStart = Date.now();
        this.responseTimers.speechEnd = Date.now();
        
        // 🧹 Limpiar indicador de tiempo de respuesta para nueva medición
        this.elements.responseTime.textContent = 'Midiendo...';
        this.elements.responseTime.className = 'metric-value processing';
        
        // 💬 Mostrar mensaje del usuario inmediatamente en el chat
        this.addMessage(message, true);
        
        // 📋 Crear ítem de conversación en el formato que espera OpenAI
        this.sendClientEvent({
            type: "conversation.item.create",
            item: {
                type: "message",
                role: "user",        // 👤 Especificar que es del usuario
                content: [{
                    type: "input_text",
                    text: message    // 📝 El texto del mensaje
                }]
            }
        });
        
        // 🚀 Solicitar que OpenAI genere una respuesta
        this.sendClientEvent({
            type: "response.create"
        });
        
        // ⏳ Mostrar indicador de que está procesando
        this.showTypingIndicator();
        
        this.log(`💬 Mensaje enviado: "${message}"`, 'info');
    }

    /**
     * ⏱️ Calcula y muestra los tiempos de respuesta en la interfaz
     */
    calculateAndShowResponseTime() {
        // 🔍 Debug: Mostrar estado actual de los timers
        this.log(`🔍 Timers estado: speechEnd=${this.responseTimers.speechEnd}, responseStart=${this.responseTimers.responseStart}, textStart=${this.responseTimers.textStart}, audioStart=${this.responseTimers.audioStart}, textEnd=${this.responseTimers.textEnd}, audioEnd=${this.responseTimers.audioEnd}`, 'debug');
        
        const times = {};
        
        // 🔄 Tiempo hasta que empieza a generar respuesta
        if (this.responseTimers.speechEnd && this.responseTimers.responseStart) {
            times.processingTime = this.responseTimers.responseStart - this.responseTimers.speechEnd;
        }
        
        // 📝 Tiempo hasta primer token (texto o audio)
        const firstResponseTime = this.responseTimers.textStart || this.responseTimers.audioStart;
        if (this.responseTimers.speechEnd && firstResponseTime) {
            times.timeToFirstToken = firstResponseTime - this.responseTimers.speechEnd;
        }
        
        // ✅ Tiempo total de respuesta (priorizar el que termine último)
        const responseEndTime = this.responseTimers.textEnd || this.responseTimers.audioEnd || this.responseTimers.responseEnd;
        if (this.responseTimers.speechEnd && responseEndTime) {
            times.totalResponseTime = responseEndTime - this.responseTimers.speechEnd;
        }
        
        // 🎯 Actualizar interfaz con los tiempos calculados (incluso si no están todos)
        this.updateResponseTimeDisplay(times);
        
        // 📊 Log detallado de rendimiento
        if (times.totalResponseTime) {
            this.log(`⏱️ Tiempo total de respuesta: ${times.totalResponseTime}ms`, 'info');
        }
        if (times.timeToFirstToken) {
            this.log(`🚀 Tiempo al primer token: ${times.timeToFirstToken}ms`, 'info');
        }
        if (times.processingTime) {
            this.log(`⚙️ Tiempo de procesamiento: ${times.processingTime}ms`, 'info');
        }
        
        // 🧹 Solo resetear timers cuando tengamos una respuesta completa
        if (times.totalResponseTime) {
            this.resetResponseTimers();
        }
    }

    /**
     * 🔄 Resetea los timers de respuesta para nueva medición
     */
    resetResponseTimers() {
        this.responseTimers = {
            speechStart: null,
            speechEnd: null,
            responseStart: null,
            responseEnd: null,
            textStart: null,
            textEnd: null,
            audioStart: null,
            audioEnd: null,
        };
    }

    /**
     * 📊 Actualiza la visualización de tiempos de respuesta en la interfaz
     */
    updateResponseTimeDisplay(times) {
        if (!this.elements.responseTime) return;
        
        let displayText = '';
        let colorClass = '';
        
        // 🏆 Priorizar mostrar tiempo total si está disponible
        if (times.totalResponseTime) {
            displayText = `${times.totalResponseTime}ms`;
            
            // 🎨 Código de colores basado en rendimiento
            if (times.totalResponseTime < 1000) {
                colorClass = 'excellent'; // 🟢 Excelente < 1s
            } else if (times.totalResponseTime < 2000) {
                colorClass = 'good';      // 🟡 Bueno < 2s
            } else if (times.totalResponseTime < 5000) {
                colorClass = 'fair';      // 🟠 Regular < 5s
            } else {
                colorClass = 'poor';      // 🔴 Lento > 5s
            }
        } 
        // 🚀 Si no hay tiempo total, mostrar tiempo al primer token
        else if (times.timeToFirstToken) {
            displayText = `${times.timeToFirstToken}ms (parcial)`;
            colorClass = 'processing';
        }
        // ⚙️ Si solo hay tiempo de procesamiento, mostrarlo
        else if (times.processingTime) {
            displayText = `${times.processingTime}ms (procesando)`;
            colorClass = 'processing';
        }
        // 📝 Si no hay datos, mostrar estado por defecto
        else {
            displayText = '--';
            colorClass = '';
        }
        
        this.elements.responseTime.className = `metric-value ${colorClass}`;
        this.elements.responseTime.textContent = displayText;
        
        // 📝 Tooltip con detalles adicionales
        let tooltip = '';
        if (times.totalResponseTime) {
            tooltip = `Tiempo total: ${times.totalResponseTime}ms`;
        }
        if (times.timeToFirstToken) {
            tooltip += (tooltip ? '\n' : '') + `Primer token: ${times.timeToFirstToken}ms`;
        }
        if (times.processingTime) {
            tooltip += (tooltip ? '\n' : '') + `Procesamiento: ${times.processingTime}ms`;
        }
        
        this.elements.responseTime.title = tooltip || 'Tiempo de respuesta';
    }
    
    /**
     * 🆔 Genera un ID único para eventos usando timestamp y números aleatorios
     * Cada evento necesita un ID único para tracking y debugging
     */
    generateEventId() {
        return 'event_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * 🎨 Actualiza toda la interfaz de usuario según el estado actual
     * Centraliza el control visual de botones, textos e indicadores
     */
    updateUI() {
        // 🔗 Estado de conexión visual
        const isConnected = this.isSessionActive;
        this.elements.connectionStatus.className = `status-dot ${
            isConnected ? 'connected' : 'disconnected'  // 🟢 Verde si conectado, 🔴 rojo si no
        }`;
        
        this.elements.statusText.textContent = isConnected ? 'Conectado' : 'Desconectado';
        
        // 🎮 Estados de botones principales
        this.elements.startBtn.disabled = this.isSessionActive || this.isConnecting;
        this.elements.stopBtn.disabled = !this.isSessionActive && !this.isConnecting;
        
        // ⌨️ Habilitar/deshabilitar inputs de texto según conexión
        this.elements.textInput.disabled = !this.isSessionActive;
        this.elements.sendTextBtn.disabled = !this.isSessionActive;
        
        // ⚙️ Deshabilitar configuración durante sesión activa
        if (this.elements.sampleRate) {
            this.elements.sampleRate.disabled = this.isSessionActive || this.isConnecting;
        }
        if (this.elements.bitrate) {
            this.elements.bitrate.disabled = this.isSessionActive || this.isConnecting;
        }
        
        // 📝 Actualizar texto de botones según estado
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
     * 📝 Sistema de logging mejorado con colores, iconos y mejor formato
     * Proporciona feedback visual detallado para debugging y monitoreo
     */
    log(message, type = 'info') {
        // ✋ Solo crear elementos de log si el contenedor existe
        if (!this.elements.logContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        
        // 🎨 Iconos y colores específicos para cada tipo de mensaje
        const logTypes = {
            'info': { icon: '💡', label: 'INFO', color: '#3b82f6' },      // 🔵 Azul - información
            'success': { icon: '✅', label: 'SUCCESS', color: '#10b981' }, // 🟢 Verde - éxito
            'warning': { icon: '⚠️', label: 'WARNING', color: '#f59e0b' }, // 🟡 Amarillo - advertencia
            'error': { icon: '❌', label: 'ERROR', color: '#ef4444' },     // 🔴 Rojo - error
            'debug': { icon: '🔍', label: 'DEBUG', color: '#8b5cf6' }      // 🟣 Púrpura - debug
        };
        
        const logType = logTypes[type] || logTypes['info'];
        
        // 🏗️ Construir HTML del log con estructura visual
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
        
        // 📋 Agregar al contenedor y hacer scroll automático
        this.elements.logContainer.appendChild(logEntry);
        this.elements.logContainer.scrollTop = this.elements.logContainer.scrollHeight;
        
        // 🧹 Limitar entradas del log para evitar usar demasiada memoria
        const entries = this.elements.logContainer.children;
        if (entries.length > 100) {
            this.elements.logContainer.removeChild(entries[0]); // Eliminar el más antiguo
        }
        
        // 🖥️ También enviar a la consola del navegador con colores
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

// 🚀 Inicializar la aplicación cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    // 🎯 Crear instancia global del cliente para poder acceder desde la consola
    window.realtimeClient = new OpenAIRealtimeClient();
    
    // 🛠️ Exponer función útil para testing desde la consola del navegador
    // Permite enviar mensajes rápidamente escribiendo: sendMessage("hola")
    window.sendMessage = (message) => {
        if (window.realtimeClient.isSessionActive) {
            window.realtimeClient.sendTextMessage(message);
        } else {
            console.log('❌ Sesión no activa. Inicia una sesión primero.');
        }
    };
    
    // 🧪 Función de test para verificar el sistema de medición de tiempos
    window.testTimers = () => {
        const client = window.realtimeClient;
        console.log('🧪 Iniciando test de timers...');
        
        // Simular flujo de medición de tiempo
        client.responseTimers.speechStart = Date.now() - 3000;
        client.responseTimers.speechEnd = Date.now() - 2000;
        client.responseTimers.responseStart = Date.now() - 1500;
        client.responseTimers.textStart = Date.now() - 1000;
        client.responseTimers.textEnd = Date.now();
        
        console.log('📊 Timers simulados:', client.responseTimers);
        client.calculateAndShowResponseTime();
        console.log('✅ Test completado. Revisa el indicador de tiempo de respuesta.');
    };
    
    // 📝 Logs informativos para desarrolladores
    console.log('🎤 Cliente OpenAI Realtime inicializado');
    console.log('💡 Usa sendMessage("tu mensaje") para enviar mensajes de texto');
    console.log('🧪 Usa testTimers() para probar el sistema de medición de tiempos');
    console.log('🔍 Usa window.realtimeClient para acceder a la instancia completa');
});
