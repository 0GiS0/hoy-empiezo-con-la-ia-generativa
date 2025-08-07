import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Configuración del servidor
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Configuración de audio
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo para archivos
    
    # Configuración de OpenAI
    WHISPER_MODEL = "whisper-1"
    CHAT_MODEL = "gpt-4o-mini"
    TTS_MODEL = "tts-1"
    TTS_VOICE = "nova"
    
    # Configuración de conversación
    MAX_TOKENS = 150
    TEMPERATURE = 0.7
    
    @staticmethod
    def validate():
        """Validar que todas las configuraciones necesarias estén presentes"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY es requerida")
        return True
