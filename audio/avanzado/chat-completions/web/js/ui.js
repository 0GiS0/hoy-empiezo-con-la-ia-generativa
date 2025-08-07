/**
 * Módulo para manejar la interfaz de usuario
 */
class UIManager {
    constructor() {
        this.modals = {};
        this.initializeEventListeners();
    }

    /**
     * Inicializar event listeners
     */
    initializeEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupButtons();
            this.setupModals();
            this.setupKeyboardShortcuts();
        });
    }

    /**
     * Configurar botones
     */
    setupButtons() {
        // Botón limpiar conversación
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.showConfirmModal(
                    '¿Estás seguro de que quieres limpiar toda la conversación?',
                    () => {
                        if (window.conversation) {
                            window.conversation.clearConversation();
                        }
                    }
                );
            });
        }

        // Botón exportar
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                if (window.conversation) {
                    window.conversation.exportConversation();
                }
            });
        }
    }

    /**
     * Configurar modales
     */
    setupModals() {
        // Botones de cerrar
        const closeButtons = document.querySelectorAll('.close-btn');
        closeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Cerrar modal al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });

        // Configurar modal de confirmación
        const confirmYes = document.getElementById('confirmYes');
        if (confirmYes) {
            confirmYes.addEventListener('click', () => {
                if (this.confirmCallback) {
                    this.confirmCallback();
                    this.confirmCallback = null;
                }
                this.closeModal('confirmModal');
            });
        }
    }

    /**
     * Configurar atajos de teclado
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Escape para cerrar modales
            if (e.key === 'Escape') {
                this.closeAllModals();
            }

            // Ctrl+Enter para exportar
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                if (window.conversation) {
                    window.conversation.exportConversation();
                }
            }

            // Ctrl+Shift+C para limpiar
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                document.getElementById('clearBtn')?.click();
            }
        });
    }

    /**
     * Mostrar modal de error
     */
    showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        const errorModal = document.getElementById('errorModal');
        
        if (errorMessage && errorModal) {
            errorMessage.textContent = message;
            this.showModal('errorModal');
        } else {
            // Fallback a alert si no hay modal
            alert('Error: ' + message);
        }
    }

    /**
     * Mostrar modal de confirmación
     */
    showConfirmModal(message, callback) {
        const confirmMessage = document.getElementById('confirmMessage');
        const confirmModal = document.getElementById('confirmModal');
        
        if (confirmMessage && confirmModal) {
            confirmMessage.textContent = message;
            this.confirmCallback = callback;
            this.showModal('confirmModal');
        } else {
            // Fallback a confirm si no hay modal
            if (confirm(message)) {
                callback();
            }
        }
    }

    /**
     * Mostrar modal
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            
            // Focus en el primer elemento focuseable
            const focusableElement = modal.querySelector('button, input, textarea, select');
            if (focusableElement) {
                setTimeout(() => focusableElement.focus(), 100);
            }
        }
    }

    /**
     * Cerrar modal
     */
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    /**
     * Cerrar todos los modales
     */
    closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    /**
     * Mostrar notificación toast
     */
    showToast(message, type = 'info', duration = 3000) {
        // Crear o obtener contenedor de toasts
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(toastContainer);
        }

        // Crear toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            background: ${this.getToastColor(type)};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease-out;
            max-width: 300px;
            word-wrap: break-word;
        `;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Animación de entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remover
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    /**
     * Obtener color del toast
     */
    getToastColor(type) {
        switch (type) {
            case 'success': return '#28a745';
            case 'error': return '#dc3545';
            case 'warning': return '#ffc107';
            case 'info': 
            default: return '#17a2b8';
        }
    }

    /**
     * Mostrar loader global
     */
    showLoader(show = true) {
        let loader = document.getElementById('globalLoader');
        
        if (show && !loader) {
            loader = document.createElement('div');
            loader.id = 'globalLoader';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9998;
            `;
            
            loader.innerHTML = `
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 15px;
                ">
                    <div class="spinner"></div>
                    <span>Cargando...</span>
                </div>
            `;
            
            document.body.appendChild(loader);
        } else if (!show && loader) {
            loader.remove();
        }
    }

    /**
     * Actualizar estado de la aplicación
     */
    updateAppState(state) {
        const body = document.body;
        
        // Remover clases de estado previas
        body.classList.remove('recording', 'processing', 'playing');
        
        // Agregar nueva clase de estado
        if (state) {
            body.classList.add(state);
        }
    }

    /**
     * Verificar compatibilidad del navegador
     */
    checkBrowserCompatibility() {
        const issues = [];

        // Verificar MediaRecorder
        if (!window.MediaRecorder) {
            issues.push('Tu navegador no soporta la grabación de audio');
        }

        // Verificar getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            issues.push('Tu navegador no soporta el acceso al micrófono');
        }

        // Verificar Audio
        if (!window.Audio) {
            issues.push('Tu navegador no soporta la reproducción de audio');
        }

        // Verificar fetch
        if (!window.fetch) {
            issues.push('Tu navegador no soporta las funcionalidades de red requeridas');
        }

        if (issues.length > 0) {
            this.showError(
                'Problemas de compatibilidad detectados:\n\n' + 
                issues.join('\n') + 
                '\n\nPor favor, actualiza tu navegador o usa uno más moderno.'
            );
            return false;
        }

        return true;
    }

    /**
     * Inicializar tooltips
     */
    initializeTooltips() {
        const elementsWithTooltips = document.querySelectorAll('[title]');
        
        elementsWithTooltips.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.getAttribute('title'));
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    /**
     * Mostrar tooltip
     */
    showTooltip(element, text) {
        let tooltip = document.getElementById('tooltip');
        
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 0.8rem;
                z-index: 10000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
            `;
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = text;
        tooltip.style.opacity = '1';

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    }

    /**
     * Ocultar tooltip
     */
    hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
        }
    }
}

// Exportar para uso global
window.UIManager = UIManager;

// Función global para mostrar errores
window.showError = function(message) {
    if (window.ui) {
        window.ui.showError(message);
    } else {
        console.error(message);
        alert(message);
    }
};

// Función global para cerrar modales
window.closeModal = function(modalId) {
    if (window.ui) {
        window.ui.closeModal(modalId);
    }
};
