#!/bin/bash

# Script para configurar e iniciar el servidor de audio WebRTC

echo "🎤 Configurando servidor de audio WebRTC..."

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

# Verificar instalación de aiortc
python3 -c "import aiortc" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias adicionales para aiortc..."
    
    # En sistemas Debian/Ubuntu
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
    fi
    
    # Reinstalar aiortc
    pip3 install --force-reinstall aiortc
fi

echo "🚀 Iniciando servidor WebRTC..."
echo "📡 Servidor disponible en: ws://localhost:8765"
echo "🌐 Frontend disponible en: ../web/index.html"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Ejecutar servidor con logs
python3 server.py 2>&1 | tee logs/server.log
