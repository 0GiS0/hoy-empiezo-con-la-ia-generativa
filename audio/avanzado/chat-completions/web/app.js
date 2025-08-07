/**
 * 🎤 Chat por Voz - Versión Simplificada
 */
class SimpleVoiceChat {
    constructor() {
        this.API_BASE_URL = 'http://127.0.0.1:5000';
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.audioStorage = new Map(); // Para guardar todos los audios
        this.currentAudio = null; // Audio actualmente reproduciéndose
        this.init();
    }

    async init() {
        this.setupEventListeners();
        console.log('✅ App iniciada');
    }

    setupEventListeners() {
        const recordBtn = document.getElementById('recordBtn');
        
        // Eventos del botón
        recordBtn.addEventListener('mousedown', () => this.startRecording());
        recordBtn.addEventListener('mouseup', () => this.stopRecording());
        recordBtn.addEventListener('mouseleave', () => {
            if (this.isRecording) this.stopRecording();
        });

        // Eventos de teclado (barra espaciadora)
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !this.isRecording) {
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
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioChunks = [];
            this.mediaRecorder = new MediaRecorder(this.stream);

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => this.processRecording();

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateUI(true);

        } catch (error) {
            console.error('Error grabando:', error);
            alert('Error accediendo al micrófono');
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.mediaRecorder.stop();
        this.isRecording = false;
        this.updateUI(false);
    }

    updateUI(isRecording) {
        const recordBtn = document.getElementById('recordBtn');
        const instructions = document.getElementById('instructions');
        
        if (recordBtn) {
            recordBtn.classList.toggle('recording', isRecording);
            recordBtn.innerHTML = isRecording ? '<i class="fas fa-stop"></i>' : '<i class="fas fa-microphone"></i>';
        }
        
        if (instructions) {
            instructions.textContent = isRecording ? 'Grabando... Suelta para enviar' : 'Mantén presionado el botón o la barra espaciadora para grabar';
        }
    }

    async processRecording() {
        if (this.audioChunks.length === 0) return;

        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        // Guardar el audio del usuario para reproducción posterior
        const userAudioUrl = URL.createObjectURL(audioBlob);
        
        await this.sendAudioToAPI(audioBlob, userAudioUrl);
    }

    async sendAudioToAPI(audioBlob, userAudioUrl) {
        const startTime = Date.now();
        let processingMessage = null;
        
        try {
            // Mostrar mensaje de procesamiento
            processingMessage = this.addMessage('assistant', '⏳ Procesando tu audio...');
            
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            const response = await fetch(`${this.API_BASE_URL}/conversation`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error(`Error: ${response.status}`);

            const audioArrayBuffer = await response.arrayBuffer();
            const responseAudioBlob = new Blob([audioArrayBuffer], { type: 'audio/wav' });
            const responseAudioUrl = URL.createObjectURL(responseAudioBlob);

            // Calcular tiempo transcurrido
            const endTime = Date.now();
            const duration = ((endTime - startTime) / 1000).toFixed(1);

            // Remover mensaje de procesamiento
            if (processingMessage) {
                processingMessage.remove();
            }

            // Añadir mensajes con audio reproducible
            this.addMessage('user', '🎤 Audio enviado', userAudioUrl);
            this.addMessage('assistant', `🔊 Respuesta recibida (${duration}s)`, responseAudioUrl);
            
            // Reproducir automáticamente la respuesta
            this.playAudio(responseAudioUrl);

        } catch (error) {
            // Remover mensaje de procesamiento en caso de error
            if (processingMessage) {
                processingMessage.remove();
            }
            
            const endTime = Date.now();
            const duration = ((endTime - startTime) / 1000).toFixed(1);
            
            console.error('Error:', error);
            this.addMessage('assistant', `❌ Error después de ${duration}s: ${error.message}`);
            
            // Limpiar URL del usuario en caso de error
            if (userAudioUrl) {
                // Solo revocar si no se guardó en el storage
                const userAudioStored = Array.from(this.audioStorage.values()).includes(userAudioUrl);
                if (!userAudioStored) {
                    URL.revokeObjectURL(userAudioUrl);
                }
            }
        }
    }

    async playAudio(audioUrl) {
        // Parar cualquier audio que se esté reproduciendo
        this.stopCurrentAudio();
        
        // Encontrar el botón correspondiente a este audio
        const audioId = this.findAudioIdByUrl(audioUrl);
        
        const audio = new Audio(audioUrl);
        this.currentAudio = audio;
        
        // Marcar el botón como reproduciéndose si existe
        if (audioId) {
            this.updateAudioButton(audioId, true);
        }
        
        audio.onended = () => {
            this.currentAudio = null;
            if (audioId) {
                this.updateAudioButton(audioId, false);
            }
        };
        
        await audio.play();
    }

    findAudioIdByUrl(audioUrl) {
        for (const [id, url] of this.audioStorage.entries()) {
            if (url === audioUrl) {
                return id;
            }
        }
        return null;
    }

    playStoredAudio(audioId) {
        // Parar cualquier audio que se esté reproduciendo
        this.stopCurrentAudio();
        
        const audioUrl = this.audioStorage.get(audioId);
        if (audioUrl) {
            const audio = new Audio(audioUrl);
            this.currentAudio = audio;
            
            audio.onended = () => {
                this.currentAudio = null;
                this.updateAudioButton(audioId, false);
            };
            
            this.updateAudioButton(audioId, true);
            audio.play();
        }
    }

    stopCurrentAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio = null;
            
            // Actualizar todos los botones para mostrar estado "play"
            document.querySelectorAll('.audio-btn').forEach(btn => {
                btn.innerHTML = '<i class="fas fa-play"></i> Reproducir';
                btn.style.background = '#374151';
                btn.style.minWidth = '120px';
            });
        }
    }

    updateAudioButton(audioId, isPlaying) {
        const button = document.querySelector(`[data-audio-id="${audioId}"]`);
        if (button) {
            if (isPlaying) {
                button.innerHTML = '<i class="fas fa-pause"></i> Pausar';
                button.style.background = '#dc2626';
                button.style.minWidth = '120px';
            } else {
                button.innerHTML = '<i class="fas fa-play"></i> Reproducir';
                button.style.background = '#374151';
                button.style.minWidth = '120px';
            }
        }
    }

    addMessage(role, content, audioUrl = null) {
        const conversationHistory = document.getElementById('conversationHistory');
        if (!conversationHistory) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;
        
        let audioButton = '';
        if (audioUrl) {
            // Generar ID único para este audio
            const audioId = `audio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            // Guardar el audio en el storage
            this.audioStorage.set(audioId, audioUrl);
            
            audioButton = `
                <div class="audio-controls" style="margin-top: 8px;">
                    <button class="audio-btn" data-audio-id="${audioId}" 
                            onclick="voiceChat.handleAudioClick('${audioId}')" 
                            style="background: #374151; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; display: inline-flex; align-items: center; gap: 6px; min-width: 120px; justify-content: center;">
                        <i class="fas fa-play"></i> Reproducir
                    </button>
                </div>
            `;
        }
        
        if (role === 'user') {
            messageElement.innerHTML = `
                <div class="user-message">
                    <div class="message-content">${content}</div>
                    ${audioButton}
                </div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="assistant-message">
                    <div class="message-content">${content}</div>
                    ${audioButton}
                </div>
            `;
        }

        conversationHistory.appendChild(messageElement);
        conversationHistory.scrollTop = conversationHistory.scrollHeight;
        
        return messageElement;
    }

    handleAudioClick(audioId) {
        const button = document.querySelector(`[data-audio-id="${audioId}"]`);
        const isCurrentlyPlaying = this.currentAudio && button.innerHTML.includes('pause');
        
        if (isCurrentlyPlaying) {
            // Pausar audio actual
            this.stopCurrentAudio();
        } else {
            // Reproducir este audio
            this.playStoredAudio(audioId);
        }
    }

}

// Inicializar cuando el DOM esté listo
let voiceChat;
document.addEventListener('DOMContentLoaded', () => {
    voiceChat = new SimpleVoiceChat();
});

// Exponer globalmente
window.voiceChat = voiceChat;

