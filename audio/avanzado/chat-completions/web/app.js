/**
 * 🎤 Chat por Voz - Aplicación Simple
 * Demostración básica de conversación por voz con OpenAI Chat Completions API
 * 
 * @author Gisela Torres
 * @version 1.0.0
 */

class SimpleVoiceChat {
    constructor() {
        // Configuración de la API
        this.API_BASE_URL = 'http://127.0.0.1:5000';
        
        // Estado de la aplicación
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.currentAudio = null;
        
        // Inicializar aplicación
        this.init();
    }

    /**
     * 🚀 Inicializar aplicación
     */
    async init() {
        try {
            console.log('🎤 Iniciando aplicación de chat por voz...');
            
            // Configurar event listeners
            this.setupEventListeners();
            
            // Verificar estado de la API
            await this.checkApiHealth();
            
            // Verificar compatibilidad del navegador
            if (!this.checkBrowserSupport()) {
                this.showError('Tu navegador no soporta las funciones necesarias para esta aplicación.');
                return;
            }
            
            console.log('✅ Aplicación inicializada correctamente');
            
        } catch (error) {
            console.error('❌ Error inicializando aplicación:', error);
            this.showError('Error inicializando la aplicación: ' + error.message);
        }
    }

    /**
     * 🎛️ Configurar event listeners
     */
    setupEventListeners() {
        const recordBtn = document.getElementById('recordBtn');
        
        if (!recordBtn) {
            console.error('❌ Botón de grabación no encontrado');
            return;
        }

        // Eventos para mantener presionado (mouse)
        recordBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        
        recordBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        recordBtn.addEventListener('mouseleave', () => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });
      

        // Prevenir comportamiento por defecto del click
        recordBtn.addEventListener('click', (e) => {
            e.preventDefault();
        });

        // Atajo de teclado (barra espaciadora)
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isRecording && !this.isTyping()) {
                e.preventDefault();
                this.startRecording();
            }
        });

        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space' && this.isRecording) {
                e.preventDefault();
                this.stopRecording();
            }
        });

        // Manejar errores globales
        window.addEventListener('error', (e) => {
            console.error('❌ Error global:', e.error);
        });

        // Manejar promesas rechazadas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('❌ Promesa rechazada:', e.reason);
        });
    }

    /**
     * ⌨️ Verificar si el usuario está escribiendo
     */
    isTyping() {
        const activeElement = document.activeElement;
        return activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.contentEditable === 'true'
        );
    }

    /**
     * 🔍 Verificar soporte del navegador
     */
    checkBrowserSupport() {
        const isSupported = !!(
            navigator.mediaDevices && 
            navigator.mediaDevices.getUserMedia && 
            window.MediaRecorder &&
            window.Audio
        );

        if (!isSupported) {
            console.warn('⚠️ Navegador no compatible');
        }

        return isSupported;
    }

    /**
     * 🏥 Verificar estado de la API
     */
    async checkApiHealth() {
        try {
            console.log('🔍 Verificando estado de la API...');
            
            const response = await fetch(`${this.API_BASE_URL}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateConnectionStatus(true, 'API funcionando correctamente');
                console.log('✅ API conectada:', data.message);
            } else {
                throw new Error(`API no disponible: ${response.status}`);
            }
        } catch (error) {
            console.warn('⚠️ API no disponible:', error.message);
            this.updateConnectionStatus(false, 'API no disponible');
            this.showError(`La API no está disponible. Verifica que el servidor esté ejecutándose en ${this.API_BASE_URL}`);
        }
    }

    /**
     * 🔗 Actualizar estado de conexión
     */
    updateConnectionStatus(isConnected, message = '') {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (statusDot) {
            statusDot.className = `status-dot ${isConnected ? 'connected' : ''}`;
        }
        
        if (statusText) {
            statusText.textContent = message || (isConnected ? 'Conectado' : 'Desconectado');
        }

        // Log del estado
        console.log(`🔗 Estado de conexión: ${isConnected ? '✅ Conectado' : '❌ Desconectado'} - ${message}`);
    }

    /**
     * 🎙️ Inicializar stream de audio
     */
    async initAudioStream() {
        try {
            console.log('🎙️ Solicitando acceso al micrófono...');
            
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                }
            });
            
            console.log('✅ Acceso al micrófono concedido');
            return true;
            
        } catch (error) {
            console.error('❌ Error accediendo al micrófono:', error);
            this.handleMicrophoneError(error);
            return false;
        }
    }

    /**
     * 🚨 Manejar errores del micrófono
     */
    handleMicrophoneError(error) {
        let message = 'No se pudo acceder al micrófono. ';
        
        switch (error.name) {
            case 'NotAllowedError':
                message += 'Por favor, permite el acceso al micrófono en tu navegador.';
                break;
            case 'NotFoundError':
                message += 'No se encontró ningún micrófono conectado.';
                break;
            case 'NotSupportedError':
                message += 'Tu navegador no soporta la grabación de audio.';
                break;
            case 'NotReadableError':
                message += 'El micrófono está siendo usado por otra aplicación.';
                break;
            default:
                message += `Error: ${error.message}`;
        }

        console.error('🚨 Error de micrófono:', message);
        this.showError(message);
    }

    /**
     * ▶️ Iniciar grabación
     */
    async startRecording() {
        if (this.isRecording) {
            console.warn('⚠️ Ya se está grabando');
            return;
        }

        try {
            console.log('🎤 Iniciando grabación...');

            // Inicializar stream si no existe
            if (!this.stream) {
                const success = await this.initAudioStream();
                if (!success) return;
            }

            // Limpiar chunks anteriores
            this.audioChunks = [];

            // Configurar MediaRecorder
            const mimeType = this.getSupportedMimeType();
            this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });

            // Event listeners del MediaRecorder
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                console.log('🛑 MediaRecorder detenido, procesando...');
                this.processRecording();
            };

            this.mediaRecorder.onerror = (error) => {
                console.error('❌ Error en MediaRecorder:', error);
                this.showError('Error en la grabación de audio');
                this.stopRecording();
            };

            // Iniciar grabación
            this.mediaRecorder.start(100); // Recopilar datos cada 100ms
            this.isRecording = true;

            // Actualizar interfaz
            this.updateRecordingUI(true);
            
            console.log('✅ Grabación iniciada');

        } catch (error) {
            console.error('❌ Error iniciando grabación:', error);
            this.handleMicrophoneError(error);
        }
    }

    /**
     * ⏹️ Detener grabación
     */
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }

        try {
            console.log('⏹️ Deteniendo grabación...');
            
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Actualizar interfaz
            this.updateRecordingUI(false);
            
            console.log('✅ Grabación detenida');
            
        } catch (error) {
            console.error('❌ Error deteniendo grabación:', error);
            this.isRecording = false;
            this.updateRecordingUI(false);
        }
    }

    /**
     * 🎨 Actualizar interfaz de grabación
     */
    updateRecordingUI(isRecording) {
        const recordBtn = document.getElementById('recordBtn');
        const instructions = document.getElementById('instructions');
        
        if (recordBtn) {
            if (isRecording) {
                recordBtn.classList.add('recording');
                recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
                recordBtn.setAttribute('aria-label', 'Detener grabación');
            } else {
                recordBtn.classList.remove('recording');
                recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                recordBtn.setAttribute('aria-label', 'Iniciar grabación');
            }
        }
        
        if (instructions) {
            instructions.textContent = isRecording 
                ? 'Grabando... Suelta para procesar y enviar' 
                : 'Mantén presionado el botón para grabar (o usa la barra espaciadora)';
        }
    }

    /**
     * 🔄 Procesar grabación
     */
    async processRecording() {
        if (this.audioChunks.length === 0) {
            console.warn('⚠️ No hay datos de audio para procesar');
            this.showError('No se grabó audio. Intenta de nuevo.');
            return;
        }

        try {
            console.log('🔄 Procesando grabación...');
            
            // Crear blob de audio
            const mimeType = this.getSupportedMimeType();
            const audioBlob = new Blob(this.audioChunks, { type: mimeType });

            // Verificar que el audio tiene contenido suficiente
            if (audioBlob.size < 1000) { // Menos de 1KB
                console.warn('⚠️ Audio muy corto, ignorando');
                this.showError('Audio muy corto. Intenta grabar un mensaje más largo.');
                return;
            }

            console.log(`✅ Audio procesado: ${audioBlob.size} bytes, tipo: ${mimeType}`);
            
            // Enviar a la API
            await this.sendAudioToAPI(audioBlob);

        } catch (error) {
            console.error('❌ Error procesando audio:', error);
            this.showError('Error procesando el audio: ' + error.message);
        }
    }

    /**
     * 📤 Enviar audio a la API
     */
    async sendAudioToAPI(audioBlob) {
        try {
            console.log('📤 Enviando audio a la API...');
            
            // Mostrar estado de procesamiento
            this.showProcessing(true);

            // Crear FormData
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            // Enviar a la API
            const response = await fetch(`${this.API_BASE_URL}/conversation`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errorMessage = `Error del servidor: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    console.warn('No se pudo parsear respuesta de error');
                }
                throw new Error(errorMessage);
            }

            // La respuesta debe ser un archivo de audio
            const audioArrayBuffer = await response.arrayBuffer();
            
            if (audioArrayBuffer.byteLength === 0) {
                throw new Error('Respuesta de audio vacía');
            }

            console.log(`✅ Respuesta de audio recibida: ${audioArrayBuffer.byteLength} bytes`);
            
            // Crear blob de audio para reproducir
            const responseAudioBlob = new Blob([audioArrayBuffer], { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(responseAudioBlob);

            // Agregar mensaje del usuario (simulado)
            this.addMessage('user', 'Audio enviado correctamente');

            // Reproducir respuesta
            await this.playAudioResponse(audioUrl);

        } catch (error) {
            console.error('❌ Error enviando audio:', error);
            this.showError('Error comunicándose con la API: ' + error.message);
        } finally {
            this.showProcessing(false);
        }
    }

    /**
     * 🔊 Reproducir respuesta de audio
     */
    async playAudioResponse(audioUrl) {
        try {
            console.log('🔊 Reproduciendo respuesta de la IA...');
            
            // Detener audio actual si existe
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio = null;
            }

            // Crear elemento de audio
            this.currentAudio = new Audio(audioUrl);
            
            // Agregar mensaje del asistente
            const messageElement = this.addMessage('assistant', 'Reproduciendo respuesta de audio...', audioUrl);

            // Configurar eventos del audio
            this.currentAudio.onloadstart = () => {
                console.log('📥 Cargando audio...');
            };

            this.currentAudio.oncanplay = () => {
                console.log('✅ Audio listo para reproducir');
            };

            this.currentAudio.onplay = () => {
                console.log('▶️ Reproducción iniciada');
                messageElement.classList.add('audio-playing');
                
                // Actualizar botón de reproducción si existe
                const playButton = messageElement.querySelector('.play-button');
                if (playButton) {
                    playButton.innerHTML = '<i class="fas fa-pause"></i>';
                }
            };

            this.currentAudio.onended = () => {
                console.log('✅ Reproducción completada');
                messageElement.classList.remove('audio-playing');
                
                // Actualizar contenido del mensaje
                const messageContent = messageElement.querySelector('.message-content');
                if (messageContent) {
                    messageContent.textContent = 'Respuesta de audio reproducida';
                }
                
                // Restaurar botón de reproducción
                const playButton = messageElement.querySelector('.play-button');
                if (playButton) {
                    playButton.innerHTML = '<i class="fas fa-play"></i>';
                }
                
                // Limpiar memoria
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
            };

            this.currentAudio.onerror = (error) => {
                console.error('❌ Error reproduciendo audio:', error);
                messageElement.classList.remove('audio-playing');
                
                const messageContent = messageElement.querySelector('.message-content');
                if (messageContent) {
                    messageContent.textContent = 'Error reproduciendo audio';
                }
                
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
            };

            // Reproducir
            await this.currentAudio.play();

        } catch (error) {
            console.error('❌ Error reproduciendo audio:', error);
            this.showError('Error reproduciendo respuesta de audio: ' + error.message);
        }
    }

    /**
     * 💬 Agregar mensaje a la conversación
     */
    addMessage(role, content, audioUrl = null) {
        const conversationHistory = document.getElementById('conversationHistory');
        
        if (!conversationHistory) {
            console.error('❌ Contenedor de conversación no encontrado');
            return null;
        }

        // Remover mensaje de bienvenida si existe
        const welcomeMessage = conversationHistory.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Crear elemento del mensaje
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        
        const icon = role === 'user' ? 'fas fa-user' : 'fas fa-robot';
        const title = role === 'user' ? 'Tú' : 'Asistente IA';
        const timestamp = new Date().toLocaleTimeString();
        
        // Controles de audio solo para mensajes del asistente
        let audioControls = '';
        if (audioUrl && role === 'assistant') {
            audioControls = `
                <div class="audio-controls">
                    <button class="play-button" onclick="voiceChat.replayAudio('${audioUrl}')" title="Reproducir audio">
                        <i class="fas fa-play"></i>
                    </button>
                    <span class="audio-status">
                        <i class="fas fa-music"></i> Audio disponible
                    </span>
                </div>
            `;
        }

        messageElement.innerHTML = `
            <div class="message-header">
                <i class="${icon}"></i>
                <span>${title}</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">${this.escapeHtml(content)}</div>
            ${audioControls}
        `;

        conversationHistory.appendChild(messageElement);
        
        // Scroll automático al final
        conversationHistory.scrollTop = conversationHistory.scrollHeight;

        return messageElement;
    }

    /**
     * 🔁 Reproducir audio específico
     */
    async replayAudio(audioUrl) {
        try {
            if (this.currentAudio) {
                this.currentAudio.pause();
            }
            
            this.currentAudio = new Audio(audioUrl);
            await this.currentAudio.play();
            
        } catch (error) {
            console.error('❌ Error reproduciendo audio:', error);
            this.showError('Error reproduciendo audio');
        }
    }

    /**
     * ⚙️ Obtener tipo MIME soportado
     */
    getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/wav'
        ];

        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                console.log(`✅ Tipo MIME soportado: ${type}`);
                return type;
            }
        }

        console.warn('⚠️ Ningún tipo MIME preferido soportado, usando fallback');
        return 'audio/webm'; // Fallback
    }

    /**
     * ⏳ Mostrar/ocultar estado de procesamiento
     */
    showProcessing(show) {
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
     * ❌ Mostrar error
     */
    showError(message) {
        console.error('❌ Error:', message);
        
        // Remover error anterior si existe
        const existingError = document.querySelector('.error');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear elemento de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${this.escapeHtml(message)}</span>
        `;
        
        // Agregar al contenedor principal
        const main = document.querySelector('main');
        if (main) {
            main.appendChild(errorDiv);
            
            // Auto-remover después de 8 segundos
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 8000);
            
            // Scroll para mostrar el error
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * 🛡️ Escapar HTML para prevenir XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 🧹 Limpiar recursos
     */
    cleanup() {
        console.log('🧹 Limpiando recursos...');
        
        // Detener stream de audio
        if (this.stream) {
            this.stream.getTracks().forEach(track => {
                track.stop();
                console.log('🔇 Track de audio detenido');
            });
            this.stream = null;
        }
        
        // Detener audio actual
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        
        // Detener MediaRecorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        
        console.log('✅ Recursos limpiados');
    }

    /**
     * 📊 Obtener información de estado
     */
    getState() {
        return {
            isRecording: this.isRecording,
            hasStream: !!this.stream,
            hasAudio: !!this.currentAudio,
            apiUrl: this.API_BASE_URL,
            chunksCount: this.audioChunks.length,
            timestamp: new Date().toISOString()
        };
    }
}

// === INICIALIZACIÓN ===

// Variable global para la aplicación
let voiceChat;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM cargado, inicializando aplicación...');
    voiceChat = new SimpleVoiceChat();
});

// Limpiar recursos al cerrar la página
window.addEventListener('beforeunload', () => {
    if (voiceChat) {
        voiceChat.cleanup();
    }
});

// Limpiar recursos al cambiar de página
window.addEventListener('pagehide', () => {
    if (voiceChat) {
        voiceChat.cleanup();
    }
});

// Exponer globalmente para debugging y acceso desde HTML
window.voiceChat = voiceChat;

// === UTILIDADES GLOBALES ===

/**
 * Función global para debugging
 */
window.getVoiceChatState = () => {
    return voiceChat ? voiceChat.getState() : { error: 'App not initialized' };
};

/**
 * Función global para mostrar información de compatibilidad
 */
window.checkVoiceCompatibility = () => {
    const checks = {
        mediaDevices: !!navigator.mediaDevices,
        getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        mediaRecorder: !!window.MediaRecorder,
        audio: !!window.Audio,
        fetch: !!window.fetch,
        permissions: navigator.permissions ? true : false
    };
    
    console.table(checks);
    return checks;
};
