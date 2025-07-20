/**
 * Módulo para manejar la grabación de audio
 */
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.recordButton = null;
        
        this.initializeEventListeners();
    }

    /**
     * Inicializar event listeners
     */
    initializeEventListeners() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupRecordButton());
        } else {
            this.setupRecordButton();
        }
    }

    /**
     * Configurar el botón de grabación
     */
    setupRecordButton() {
        this.recordButton = document.getElementById('recordBtn');
        if (!this.recordButton) {
            console.error('Botón de grabación no encontrado');
            return;
        }

        // Eventos para mantener presionado
        this.recordButton.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.recordButton.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        this.recordButton.addEventListener('mouseleave', (e) => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        // Eventos táctiles para dispositivos móviles
        this.recordButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.recordButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Prevenir comportamiento por defecto
        this.recordButton.addEventListener('click', (e) => {
            e.preventDefault();
        });
    }

    /**
     * Inicializar el stream de audio
     */
    async initializeAudioStream() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                }
            });
            return true;
        } catch (error) {
            console.error('Error accediendo al micrófono:', error);
            this.handleMicrophoneError(error);
            return false;
        }
    }

    /**
     * Manejar errores del micrófono
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
            default:
                message += 'Error desconocido: ' + error.message;
        }

        if (window.showError) {
            window.showError(message);
        } else {
            alert(message);
        }
    }

    /**
     * Iniciar grabación
     */
    async startRecording() {
        if (this.isRecording) return;

        try {
            // Inicializar stream si no existe
            if (!this.stream) {
                const success = await this.initializeAudioStream();
                if (!success) return;
            }

            // Limpiar chunks anteriores
            this.audioChunks = [];

            // Configurar MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: this.getSupportedMimeType()
            });

            // Event listeners del MediaRecorder
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.onerror = (error) => {
                console.error('Error en MediaRecorder:', error);
                this.stopRecording();
            };

            // Iniciar grabación
            this.mediaRecorder.start(100); // Recopilar datos cada 100ms
            this.isRecording = true;

            // Actualizar UI
            this.updateRecordingUI(true);

            console.log('Grabación iniciada');

        } catch (error) {
            console.error('Error iniciando grabación:', error);
            this.handleMicrophoneError(error);
        }
    }

    /**
     * Detener grabación
     */
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        try {
            this.mediaRecorder.stop();
            this.isRecording = false;

            // Actualizar UI
            this.updateRecordingUI(false);

            console.log('Grabación detenida');

        } catch (error) {
            console.error('Error deteniendo grabación:', error);
            this.isRecording = false;
            this.updateRecordingUI(false);
        }
    }

    /**
     * Procesar la grabación
     */
    async processRecording() {
        if (this.audioChunks.length === 0) {
            console.warn('No hay datos de audio para procesar');
            return;
        }

        try {
            // Crear blob de audio
            const audioBlob = new Blob(this.audioChunks, {
                type: this.getSupportedMimeType()
            });

            // Verificar que el audio tiene contenido
            if (audioBlob.size < 1000) { // Menos de 1KB probablemente es muy corto
                console.warn('Audio muy corto, ignorando');
                return;
            }

            console.log(`Audio procesado: ${audioBlob.size} bytes`);

            // Enviar audio para procesamiento
            if (window.conversation && window.conversation.processAudio) {
                await window.conversation.processAudio(audioBlob);
            } else {
                console.error('Módulo de conversación no disponible');
            }

        } catch (error) {
            console.error('Error procesando audio:', error);
            if (window.showError) {
                window.showError('Error procesando el audio: ' + error.message);
            }
        }
    }

    /**
     * Obtener tipo MIME soportado
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
                return type;
            }
        }

        return 'audio/webm'; // Fallback
    }

    /**
     * Actualizar UI de grabación
     */
    updateRecordingUI(isRecording) {
        const recordButton = document.getElementById('recordBtn');
        const recordingStatus = document.getElementById('recordingStatus');

        if (recordButton) {
            if (isRecording) {
                recordButton.classList.add('recording');
                recordButton.innerHTML = `
                    <i class="fas fa-stop"></i>
                    <span>Grabando... Suelta para enviar</span>
                `;
            } else {
                recordButton.classList.remove('recording');
                recordButton.innerHTML = `
                    <i class="fas fa-microphone"></i>
                    <span>Mantén presionado para hablar</span>
                `;
            }
        }

        if (recordingStatus) {
            if (isRecording) {
                recordingStatus.classList.remove('hidden');
            } else {
                recordingStatus.classList.add('hidden');
            }
        }
    }

    /**
     * Verificar soporte del navegador
     */
    static isSupported() {
        return !!(navigator.mediaDevices && 
                 navigator.mediaDevices.getUserMedia && 
                 window.MediaRecorder);
    }

    /**
     * Limpiar recursos
     */
    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
    }
}

// Exportar para uso global
window.AudioRecorder = AudioRecorder;
