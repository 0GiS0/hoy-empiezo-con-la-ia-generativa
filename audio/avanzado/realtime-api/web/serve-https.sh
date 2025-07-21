#!/bin/bash
# Script para servir la web con HTTPS usando http-server y certificados autofirmados
# Ubicación: audio/realtime-api/web/serve-https.sh

set -e

# 1. Instalar http-server si no está instalado
echo "Verificando instalación de http-server..."
if ! command -v http-server &> /dev/null; then
    echo "Instalando http-server globalmente..."
    npm install -g http-server
else
    echo "http-server ya está instalado."
fi

# 2. Generar certificados autofirmados si no existen
if [[ ! -f cert.pem || ! -f key.pem ]]; then
    echo "Generando certificados autofirmados..."
    openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem \
        -subj "/C=ES/ST=None/L=None/O=Dev/OU=Dev/CN=localhost"
else
    echo "Certificados ya existen."
fi

# 3. Servir la web con HTTPS en el puerto 8081
echo "Sirviendo la web en https://localhost:8081 ..."
http-server . -S -C cert.pem -K key.pem -p 8081
