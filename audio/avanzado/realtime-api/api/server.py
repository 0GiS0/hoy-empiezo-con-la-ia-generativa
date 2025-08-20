#!/usr/bin/env python3
"""
🔑 Servidor para generar ephemeral keys de OpenAI Realtime API

¿Qué hace este servidor?
- Expone un endpoint seguro que solicita a OpenAI una "ephemeral key" ⏳.
- Esa clave temporal permite que el navegador se conecte a la Realtime API
    sin exponer tu OPENAI_API_KEY en el front. 🛡️

Puntos clave del flujo:
1) El cliente llama a POST /api/token.
2) Este servidor pide a OpenAI una sesión Realtime con el modelo y voz deseados.
3) Devuelve al cliente la respuesta de OpenAI (con la clave temporal y configuración).
"""

# =========================
# 📦 IMPORTS Y DEPENDENCIAS
# =========================
import os
import logging
from datetime import datetime
import requests
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# 🔐 Cargar variables de entorno desde .env (OPENAI_API_KEY, HOST, PORT, etc.)
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
CORS(app)  # 🌐 Permitir CORS para requests desde el frontend (demos locales)

# 🔑 Configuración de OpenAI (API Key del servidor)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY no encontrada en las variables de entorno")
    raise ValueError("OPENAI_API_KEY es requerida")

OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime/sessions"

# 📁 Configuración de archivos estáticos: servimos la web que vive en ../web
# Útil para demos: evita configurar un servidor aparte para el frontend.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # /path/to/api/
# /path/to/realtime-api/
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
# /path/to/realtime-api/web/
WEB_DIR = os.path.join(PROJECT_DIR, 'web')

# Debug: Verificar que el directorio web existe
if not os.path.exists(WEB_DIR):
    logger.error(f"❌ Directorio web no encontrado en: {WEB_DIR}")
    logger.error(f"📁 Directorio actual del script: {SCRIPT_DIR}")
    logger.error(f"📁 Directorio del proyecto: {PROJECT_DIR}")
else:
    logger.info(f"✅ Directorio web encontrado en: {WEB_DIR}")

# =========================
# 🛣️ RUTAS DE LA API
# =========================


@app.route('/')
def index():
    """🏠 Página principal: sirve index.html del directorio web."""
    index_path = os.path.join(WEB_DIR, 'index.html')
    logger.info(f"🏠 Intentando servir index.html desde: {index_path}")

    try:
        if not os.path.exists(index_path):
            logger.error(f"❌ index.html no encontrado en: {index_path}")
            return jsonify({
                'error': 'Frontend no encontrado',
                'message': f'index.html no existe en {index_path}',
                'web_dir': WEB_DIR,
                'files_found': os.listdir(WEB_DIR) if os.path.exists(WEB_DIR) else []
            }), 404

        return send_file(index_path)
    except Exception as e:
        logger.error(f"❌ Error sirviendo index.html: {e}")
        return jsonify({
            'error': 'Error sirviendo frontend',
            'message': str(e),
            'web_dir': WEB_DIR
        }), 500


@app.route('/<path:filename>')
def serve_static(filename):
    """📁 Servir archivos estáticos (JS, CSS, assets) del directorio web."""
    file_path = os.path.join(WEB_DIR, filename)
    logger.info(f"📁 Intentando servir archivo: {file_path}")

    try:
        if not os.path.exists(file_path):
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            return jsonify({
                'error': 'Archivo no encontrado',
                'message': f'El archivo {filename} no existe en {WEB_DIR}',
                'requested_file': filename,
                'files_available': os.listdir(WEB_DIR) if os.path.exists(WEB_DIR) else []
            }), 404

        return send_from_directory(WEB_DIR, filename)
    except Exception as e:
        logger.error(f"❌ Error sirviendo archivo {filename}: {e}")
        return jsonify({
            'error': 'Error sirviendo archivo',
            'message': str(e),
            'requested_file': filename
        }), 500


@app.route('/api/token', methods=['POST'])
def get_ephemeral_key():
    """
    🔑 Genera una ephemeral key para conectarse a la API de OpenAI Realtime.

    Esta key permite al cliente conectarse directamente a OpenAI sin exponer
    la API key del servidor.

    Notas:
    - La session se crea con un modelo Realtime y parámetros (voz, instrucciones).
    - La respuesta incluye la clave temporal y su expiración.
    """
    try:
        logger.info("🔑 Solicitando ephemeral key a OpenAI...")

    # ⚙️ Configuración de la sesión Realtime (modelo, voz, instrucciones)
        session_config = {
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "voice": "verse",
            "instructions": "Eres un asistente útil. Responde de manera conversacional y natural."
        }

    # 📬 Headers para la request a OpenAI
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

    # 🔗 Hacer la request a OpenAI para obtener la sesión
        response = requests.post(
            OPENAI_REALTIME_URL,
            headers=headers,
            json=session_config,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Ephemeral key generada exitosamente")

            # 🧩 Añadimos metadatos útiles para el cliente (debug/observabilidad)
            result = {
                **data,
                'server_timestamp': datetime.now().isoformat(),
                'config_used': session_config
            }

            return jsonify(result)
        else:
            logger.error(
                f"❌ Error de OpenAI API: {response.status_code} - {response.text}")
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

# =========================
# 🏁 PUNTO DE ENTRADA MAIN
# =========================


def main():
    """🏁 Función principal para iniciar el servidor Flask."""
    try:
        logger.info("🚀 Iniciando servidor de ephemeral keys...")
        logger.info("💡 Endpoints disponibles:")
        logger.info("   GET  /               - Interfaz web")
        logger.info("   GET  /api/health     - Verificar estado del servidor")
        logger.info("   POST /api/token      - Generar ephemeral key")

        # 🧰 Configuración del servidor (HOST/PORT/DEBUG desde env con defaults)
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'

        logger.info(f"🌐 Servidor ejecutándose en http://{host}:{port}")
        logger.info(f"🎨 Interfaz web disponible en http://{host}:{port}")
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
