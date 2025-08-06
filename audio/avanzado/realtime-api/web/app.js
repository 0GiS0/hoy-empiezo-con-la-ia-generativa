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

class AudioRTCClient {
    constructor() {
        this.peerConnection = null;
        this.localStream = null;
        this.dataChannel = null;
        this.websocket = null;
        this.audioContext = null;
        this.analyser = null;
        this.isConnected = false;
        this.isStreaming = false;
        
        // Configuración
        this.config = {
            get wsUrl() {
                const proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
                // const host = window.location.hostname;
                const host = '127.0.0.1'
                const port = 8765;
                return `${proto}${host}:${port}`;
            },
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
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
            bitrate: document.getElementById('bitrate')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateUI();
        this.log('Aplicación inicializada', 'info');
    }
    
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startAudio());
        this.elements.stopBtn.addEventListener('click', () => this.stopAudio());
        
        // Detectar cambios en la configuración
        this.elements.sampleRate.addEventListener('change', () => {
            if (this.isStreaming) {
                this.log('Reiniciando para aplicar nueva configuración...', 'warning');
                this.stopAudio();
                setTimeout(() => this.startAudio(), 1000);
            }
        });
        
        this.elements.bitrate.addEventListener('change', () => {
            if (this.isStreaming) {
                this.log('Reiniciando para aplicar nueva configuración...', 'warning');
                this.stopAudio();
                setTimeout(() => this.startAudio(), 1000);
            }
        });
    }
    
    async startAudio() {
        try {
            this.log('Iniciando captura de audio...', 'info');
            // Conectar WebSocket primero
            await this.connectWebSocket();
            // Obtener stream de audio
            await this.getUserMedia();
            // Configurar WebRTC
            await this.setupWebRTC();
            // Configurar análisis de audio
            this.setupAudioAnalysis();
            // Actualizar UI
            this.isStreaming = true;
            this.updateUI();
            this.log('Audio iniciado correctamente', 'info');
        } catch (error) {
            this.log(`Error al iniciar audio: ${error && error.stack ? error.stack : error}`, 'error');
            this.stopAudio();
        }
    }

    async stopAudio() {
        this.log('Deteniendo transmisión de audio...', 'info');
        this.isStreaming = false;
        // Cerrar WebRTC
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        // Cerrar WebSocket
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        // Detener stream local
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        // Cerrar audio context
        if (this.audioContext) {
            await this.audioContext.close();
            this.audioContext = null;
        }
        this.isConnected = false;
        this.updateUI();
        this.log('Audio detenido', 'info');
    }

    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            this.log('Conectando al servidor WebSocket...', 'info');
            this.websocket = new WebSocket(this.config.wsUrl);
            this.websocket.onopen = () => {
                this.log('WebSocket conectado', 'info');
                this.isConnected = true;
                this.updateUI();
                resolve();
            };
            this.websocket.onmessage = async (event) => {
                this.log(`WebSocket mensaje recibido: ${event.data}`, 'debug');
                const data = JSON.parse(event.data);
                await this.handleWebSocketMessage(data);
            };
            this.websocket.onerror = (error) => {
                this.log(`Error en WebSocket: ${JSON.stringify(error)}`, 'error');
                reject(new Error('Error de conexión WebSocket'));
            };
            this.websocket.onclose = (event) => {
                this.log(`WebSocket desconectado (code=${event.code}, reason=${event.reason})`, 'warning');
                this.isConnected = false;
                this.updateUI();
            };
            // Timeout de conexión
            setTimeout(() => {
                if (this.websocket.readyState !== WebSocket.OPEN) {
                    reject(new Error('Timeout de conexión WebSocket'));
                }
            }, 5000);
        });
    }

    async getUserMedia() {
        const sampleRate = parseInt(this.elements.sampleRate.value);
        const constraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: sampleRate,
                channelCount: 1
            },
            video: false
        };
        this.log(`Solicitando acceso al micrófono (${sampleRate}Hz) con constraints: ${JSON.stringify(constraints)}`, 'info');
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
            this.log('Micrófono accesible', 'info');
        } catch (err) {
            this.log(`Error en getUserMedia: ${err && err.stack ? err.stack : err}`, 'error');
            throw err;
        }
    }

    async setupWebRTC() {
        this.log('Configurando WebRTC...', 'info');

        debugger;

        // Crear peer connection
        this.peerConnection = new RTCPeerConnection({
            iceServers: this.config.iceServers
        });
        // Agregar stream local
        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });
        // Configurar data channel para metadatos
        this.dataChannel = this.peerConnection.createDataChannel('audio-metadata', {
            ordered: true
        });
        this.dataChannel.onopen = () => {
            this.log('Canal de datos abierto', 'info');
            this.sendAudioConfig();
        };
        this.dataChannel.onclose = () => {
            this.log('Canal de datos cerrado', 'warning');
        };
        this.dataChannel.onerror = (e) => {
            this.log(`Error en DataChannel: ${e && e.message ? e.message : e}`, 'error');
        };
        this.dataChannel.onmessage = (e) => {
            this.log(`Mensaje recibido en DataChannel: ${e.data}`, 'debug');
        };
        // PeerConnection event listeners
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.log(`Enviando ICE candidate al servidor: ${JSON.stringify(event.candidate)}`, 'debug');
                this.websocket.send(JSON.stringify({
                    type: 'ice-candidate',
                    candidate: event.candidate
                }));
            } else {
                this.log('ICE gathering complete (no más candidates)', 'debug');
            }
        };
        this.peerConnection.onicegatheringstatechange = () => {
            this.log(`ICE gathering state: ${this.peerConnection.iceGatheringState}`, 'debug');
        };
        this.peerConnection.onsignalingstatechange = () => {
            this.log(`Signaling state: ${this.peerConnection.signalingState}`, 'debug');
        };
        this.peerConnection.onconnectionstatechange = () => {
            this.elements.connectionState.textContent = this.peerConnection.connectionState;
            this.log(`Estado de conexión: ${this.peerConnection.connectionState}`, 'info');
        };
        this.peerConnection.oniceconnectionstatechange = () => {
            this.log(`ICE connection state: ${this.peerConnection.iceConnectionState}`, 'debug');
        };
        this.peerConnection.ontrack = (event) => {
            this.log('Track recibido del servidor (no se espera en este flujo)', 'debug');
        };
        this.peerConnection.onnegotiationneeded = () => {
            this.log('onnegotiationneeded disparado', 'debug');
        };
        // Crear offer
        const offer = await this.peerConnection.createOffer();
        this.log(`Offer creado: ${JSON.stringify(offer)}`, 'debug');
        await this.peerConnection.setLocalDescription(offer);
        this.log(`LocalDescription establecida: ${JSON.stringify(this.peerConnection.localDescription)}`, 'debug');
        // Enviar offer por WebSocket
        this.log('Enviando offer al servidor...', 'debug');
        this.websocket.send(JSON.stringify({
            type: 'offer',
            offer: offer
        }));
        // Iniciar monitoreo de estadísticas
        this.startStatsMonitoring();
    }

    async handleWebSocketMessage(data) {
        this.log(`Procesando mensaje WebSocket: ${JSON.stringify(data)}`, 'debug');
        switch (data.type) {
            case 'answer':
                this.log(`Recibido answer: ${JSON.stringify(data.answer)}`, 'debug');
                await this.peerConnection.setRemoteDescription(data.answer);
                this.log('Respuesta WebRTC recibida y establecida como remoteDescription', 'info');
                break;
            case 'ice-candidate':
                this.log(`Recibido ICE candidate del servidor: ${JSON.stringify(data.candidate)}`, 'debug');
                try {
                    await this.peerConnection.addIceCandidate(data.candidate);
                    this.log('ICE candidate añadido correctamente', 'info');
                } catch (err) {
                    this.log(`Error añadiendo ICE candidate: ${err && err.stack ? err.stack : err}`, 'error');
                }
                break;
            case 'audio-processed':
                this.log(`Audio procesado: ${data.message}`, 'info');
                break;
            case 'error':
                this.log(`Error del servidor: ${data.message}`, 'error');
                break;
            default:
                this.log(`Mensaje desconocido: ${data.type}`, 'warning');
        }
    }
    
    setupAudioAnalysis() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        
        const source = this.audioContext.createMediaStreamSource(this.localStream);
        source.connect(this.analyser);
        
        this.analyser.fftSize = 256;
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const updateVolume = () => {
            if (!this.isStreaming) return;
            
            this.analyser.getByteFrequencyData(dataArray);
            
            // Calcular nivel promedio
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const percentage = Math.round((average / 255) * 100);
            
            // Actualizar UI
            this.elements.volumeFill.style.width = `${percentage}%`;
            this.elements.volumeText.textContent = `${percentage}%`;
            
            requestAnimationFrame(updateVolume);
        };
        
        updateVolume();
    }
    
    sendAudioConfig() {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            const config = {
                sampleRate: parseInt(this.elements.sampleRate.value),
                bitrate: parseInt(this.elements.bitrate.value),
                channels: 1,
                format: 'webm'
            };
            
            this.dataChannel.send(JSON.stringify({
                type: 'audio-config',
                config: config
            }));
            
            this.log(`Configuración enviada: ${JSON.stringify(config)}`, 'info');
        }
    }
    
    startStatsMonitoring() {
        const updateStats = async () => {
            if (!this.peerConnection || !this.isStreaming) return;
            
            try {
                const stats = await this.peerConnection.getStats();
                
                stats.forEach(report => {
                    if (report.type === 'outbound-rtp' && report.mediaType === 'audio') {
                        this.elements.bytesSent.textContent = this.formatBytes(report.bytesSent || 0);
                        this.elements.packetsSent.textContent = (report.packetsSent || 0).toLocaleString();
                    }
                    
                    if (report.type === 'candidate-pair' && report.state === 'succeeded') {
                        this.elements.latency.textContent = report.currentRoundTripTime ? 
                            `${Math.round(report.currentRoundTripTime * 1000)}ms` : '-';
                    }
                });
                
            } catch (error) {
                this.log(`Error obteniendo estadísticas: ${error.message}`, 'warning');
            }
            
            setTimeout(updateStats, 1000);
        };
        
        updateStats();
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    updateUI() {
        // Actualizar estado de conexión
        this.elements.connectionStatus.className = `status-indicator ${
            this.isConnected ? 'connected' : 'disconnected'
        }`;
        
        this.elements.statusText.textContent = this.isConnected ? 'Conectado' : 'Desconectado';
        
        // Actualizar botones
        this.elements.startBtn.disabled = this.isStreaming;
        this.elements.stopBtn.disabled = !this.isStreaming;
        
        // Actualizar configuración
        this.elements.sampleRate.disabled = this.isStreaming;
        this.elements.bitrate.disabled = this.isStreaming;
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="message">${escapeHTML(message)}</span>
        `;
        
        this.elements.logContainer.appendChild(logEntry);
        this.elements.logContainer.scrollTop = this.elements.logContainer.scrollHeight;
        
        // Limitar el número de entradas del log
        const entries = this.elements.logContainer.children;
        if (entries.length > 100) {
            this.elements.logContainer.removeChild(entries[0]);
        }
        
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Handler global para errores JS
window.onerror = function(message, source, lineno, colno, error) {
    alert("JS Error: " + message + " en " + source + ":" + lineno);
    console.error("JS Error:", message, source, lineno, colno, error);
};

// Log para detectar recarga de página
window.addEventListener('beforeunload', () => {
    console.log('La página se va a recargar o cerrar');
});

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new AudioRTCClient();
});
