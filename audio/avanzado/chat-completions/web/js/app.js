/**
 * Aplicación principal - Inicialización y coordinación
 */
class VoiceConversationApp {
    constructor() {
        this.audioRecorder = null;
        this.conversation = null;
        this.ui = null;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Inicializar aplicación
     */
    async init() {
        try {
            console.log('Inicializando aplicación de conversación por voz...');

            // Esperar a que el DOM esté listo
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeModules());
            } else {
                this.initializeModules();
            }

        } catch (error) {
            console.error('Error inicializando aplicación:', error);
            alert('Error inicializando la aplicación: ' + error.message);
        }
    }

    /**
     * Inicializar módulos
     */
    initializeModules() {
        try {
            // Verificar compatibilidad del navegador
            if (!this.checkCompatibility()) {
                return;
            }

            // Inicializar UI Manager
            this.ui = new UIManager();
            window.ui = this.ui;

            // Inicializar Conversation Manager
            this.conversation = new ConversationManager();
            window.conversation = this.conversation;

            // Inicializar Audio Recorder
            this.audioRecorder = new AudioRecorder();
            window.audioRecorder = this.audioRecorder;

            // Configurar event listeners globales
            this.setupGlobalEventListeners();

            // Marcar como inicializado
            this.isInitialized = true;
            
            console.log('Aplicación inicializada correctamente');
            
            // Mostrar mensaje de bienvenida
            this.showWelcomeMessage();

        } catch (error) {
            console.error('Error inicializando módulos:', error);
            if (this.ui) {
                this.ui.showError('Error inicializando la aplicación: ' + error.message);
            } else {
                alert('Error inicializando la aplicación: ' + error.message);
            }
        }
    }

    /**
     * Verificar compatibilidad del navegador
     */
    checkCompatibility() {
        const issues = [];

        // Verificar HTTPS (requerido para getUserMedia en producción)
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            issues.push('Esta aplicación requiere HTTPS para funcionar correctamente');
        }

        // Verificar MediaRecorder
        if (!window.MediaRecorder) {
            issues.push('Tu navegador no soporta la grabación de audio (MediaRecorder API)');
        }

        // Verificar getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            issues.push('Tu navegador no soporta el acceso al micrófono (getUserMedia API)');
        }

        // Verificar Web Audio API
        if (!window.AudioContext && !window.webkitAudioContext) {
            issues.push('Tu navegador no soporta la API de audio web');
        }

        // Verificar fetch
        if (!window.fetch) {
            issues.push('Tu navegador no soporta las funcionalidades de red modernas (Fetch API)');
        }

        if (issues.length > 0) {
            const message = 'Problemas de compatibilidad detectados:\n\n' + 
                          issues.join('\n') + 
                          '\n\nPor favor, usa un navegador moderno como Chrome, Firefox, Safari o Edge.';
            
            alert(message);
            return false;
        }

        return true;
    }

    /**
     * Configurar event listeners globales
     */
    setupGlobalEventListeners() {
        // Manejar errores globales
        window.addEventListener('error', (e) => {
            console.error('Error global:', e.error);
            if (this.ui) {
                this.ui.showError('Error inesperado: ' + e.error.message);
            }
        });

        // Manejar errores de promesas no capturadas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Promesa rechazada:', e.reason);
            if (this.ui) {
                this.ui.showError('Error de conexión: ' + e.reason.message);
            }
        });

        // Manejar cambios de visibilidad (pausar/reanudar cuando se cambia de pestaña)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleAppPause();
            } else {
                this.handleAppResume();
            }
        });

        // Manejar antes de cerrar la página
        window.addEventListener('beforeunload', (e) => {
            if (this.audioRecorder && this.audioRecorder.isRecording) {
                e.preventDefault();
                e.returnValue = '¿Estás seguro? Hay una grabación en progreso.';
                return e.returnValue;
            }
        });

        // Configurar atajos de teclado
        this.setupKeyboardShortcuts();
    }

    /**
     * Configurar atajos de teclado
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Barra espaciadora para grabar (solo si no se está escribiendo en un input)
            if (e.code === 'Space' && !this.isTyping()) {
                e.preventDefault();
                if (!this.audioRecorder.isRecording) {
                    this.audioRecorder.startRecording();
                }
            }

            // F1 para ayuda
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelp();
            }
        });

        document.addEventListener('keyup', (e) => {
            // Soltar barra espaciadora para detener grabación
            if (e.code === 'Space' && !this.isTyping()) {
                e.preventDefault();
                if (this.audioRecorder.isRecording) {
                    this.audioRecorder.stopRecording();
                }
            }
        });
    }

    /**
     * Verificar si el usuario está escribiendo
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
     * Manejar pausa de la aplicación
     */
    handleAppPause() {
        console.log('Aplicación pausada');
        
        // Detener grabación si está activa
        if (this.audioRecorder && this.audioRecorder.isRecording) {
            this.audioRecorder.stopRecording();
        }

        // Pausar audio si está reproduciéndose
        if (this.conversation && this.conversation.currentAudio) {
            this.conversation.currentAudio.pause();
        }
    }

    /**
     * Manejar reanudación de la aplicación
     */
    handleAppResume() {
        console.log('Aplicación reanudada');
        
        // Verificar estado de la API
        if (this.conversation) {
            this.conversation.checkApiHealth();
        }
    }

    /**
     * Mostrar mensaje de bienvenida
     */
    showWelcomeMessage() {
        // Verificar si es la primera visita
        const hasVisited = localStorage.getItem('voiceConversationVisited');
        
        if (!hasVisited) {
            setTimeout(() => {
                if (this.ui) {
                    this.ui.showToast(
                        '¡Bienvenido! Mantén presionado el botón del micrófono para hablar con la IA.',
                        'info',
                        5000
                    );
                }
                localStorage.setItem('voiceConversationVisited', 'true');
            }, 1000);
        }
    }

    /**
     * Mostrar ayuda
     */
    showHelp() {
        const helpMessage = `
Ayuda - Conversación por Voz con IA

🎤 Cómo usar:
• Mantén presionado el botón del micrófono para grabar
• Habla claramente en español
• Suelta el botón para enviar tu mensaje
• La IA responderá por texto y audio

⌨️ Atajos de teclado:
• Barra espaciadora: Grabar (mantener presionado)
• Ctrl+Enter: Exportar conversación
• Ctrl+Shift+C: Limpiar conversación
• Escape: Cerrar modales
• F1: Mostrar esta ayuda

💡 Consejos:
• Asegúrate de tener micrófono conectado
• Habla en un ambiente silencioso
• Permite el acceso al micrófono cuando se solicite
• La aplicación funciona mejor con Chrome o Firefox

🔧 Problemas comunes:
• Si no funciona el micrófono, verifica los permisos del navegador
• Si no hay respuesta, verifica la conexión a internet
• Para mejor calidad, usa auriculares
        `;

        if (this.ui) {
            this.ui.showError(helpMessage);
        } else {
            alert(helpMessage);
        }
    }

    /**
     * Obtener estado de la aplicación
     */
    getAppState() {
        return {
            isInitialized: this.isInitialized,
            isRecording: this.audioRecorder ? this.audioRecorder.isRecording : false,
            messageCount: this.conversation ? this.conversation.messageCount : 0,
            hasAudioPermission: this.audioRecorder ? !!this.audioRecorder.stream : false
        };
    }

    /**
     * Limpiar recursos
     */
    cleanup() {
        console.log('Limpiando recursos de la aplicación...');
        
        if (this.audioRecorder) {
            this.audioRecorder.cleanup();
        }

        if (this.conversation && this.conversation.currentAudio) {
            this.conversation.currentAudio.pause();
            this.conversation.currentAudio = null;
        }
    }
}

// Inicializar aplicación cuando se carga el script
window.addEventListener('load', () => {
    window.app = new VoiceConversationApp();
});

// Limpiar recursos al cerrar la página
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.cleanup();
    }
});

// Exportar para debugging
window.VoiceConversationApp = VoiceConversationApp;
