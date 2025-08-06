#!/usr/bin/env python3
"""
🔑 Servidor para generar ephemeral keys de OpenAI Realtime API
"""

# =========================
# 📦 IMPORTS Y DEPENDENCIAS
# =========================
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# =========================
# 📝 CONFIGURACIÓN DE LOGS
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# 🌐 APLICACIÓN FLASK
# =========================
app = Flask(__name__)
CORS(app)  # Permitir CORS para requests desde el frontend

# 🔑 Configuración de OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY no encontrada en las variables de entorno")
    raise ValueError("OPENAI_API_KEY es requerida")

OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime/sessions"

# =========================
# 🛣️ RUTAS DE LA API
# =========================

@app.route('/health', methods=['GET'])
def health_check():
    """🏥 Endpoint de salud para verificar que el servidor está funcionando."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'OpenAI Realtime Token Service'
    })

@app.route('/token', methods=['GET', 'POST'])
def get_ephemeral_key():
    """
    🔑 Genera una ephemeral key para conectarse a la API de OpenAI Realtime.
    
    Esta key permite al cliente conectarse directamente a OpenAI sin exponer
    la API key del servidor.
    """
    try:
        logger.info("🔑 Solicitando ephemeral key a OpenAI...")
        
        # Configuración de la sesión
        session_config = {
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "voice": "verse",
            "instructions": "Eres un asistente útil. Responde de manera conversacional y natural."
        }
        
        # Headers para la request a OpenAI
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Realizar la request a OpenAI
        response = requests.post(
            OPENAI_REALTIME_URL,
            headers=headers,
            json=session_config,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Ephemeral key generada exitosamente")
            
            # Agregar información adicional para el cliente
            result = {
                **data,
                'server_timestamp': datetime.now().isoformat(),
                'config_used': session_config
            }
            
            return jsonify(result)
        else:
            logger.error(f"❌ Error de OpenAI API: {response.status_code} - {response.text}")
            return jsonify({
                'error': 'Failed to generate ephemeral key',
                'status_code': response.status_code,
                'details': response.text
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión con OpenAI: {e}")
        return jsonify({
            'error': 'Connection error with OpenAI API',
            'details': str(e)
        }), 503
        
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/session/config', methods=['GET'])
def get_session_config():
    """⚙️ Devuelve la configuración disponible para las sesiones."""
    config = {
        'available_models': [
            'gpt-4o-realtime-preview-2024-12-17'
        ],
        'available_voices': [
            'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer', 'verse'
        ],
        'default_config': {
            'model': 'gpt-4o-realtime-preview-2024-12-17',
            'voice': 'verse',
            'temperature': 0.8,
            'max_response_output_tokens': 4096
        }
    }
    return jsonify(config)

# =========================
# 🚨 MANEJO DE ERRORES
# =========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'La ruta solicitada no existe'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Error interno del servidor'
    }), 500

# =========================
# 🏁 PUNTO DE ENTRADA MAIN
# =========================

def main():
    """🏁 Función principal para iniciar el servidor Flask."""
    try:
        logger.info("🚀 Iniciando servidor de ephemeral keys...")
        logger.info("💡 Endpoints disponibles:")
        logger.info("   GET  /health - Verificar estado del servidor")
        logger.info("   POST /token  - Generar ephemeral key")
        logger.info("   GET  /session/config - Configuración disponible")
        
        # Configuración del servidor
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Servidor ejecutándose en http://{host}:{port}")
        logger.info("💡 Presiona Ctrl+C para detener el servidor")
        
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        raise

if __name__ == "__main__":
    main()
