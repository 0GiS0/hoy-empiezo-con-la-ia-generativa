#!/usr/bin/env python3
"""
🎙️ Servidor WebRTC para procesamiento de audio en tiempo real
"""

# =========================
# 📦 IMPORTS Y DEPENDENCIAS
# =========================
import asyncio
import json
import logging
import websockets
import numpy as np
from datetime import datetime
from typing import Dict, Any
import signal
import sys
import functools
import ssl

# 📦 Librerías externas para WebRTC y procesamiento de audio
try:
    from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
    from aiortc.contrib.media import MediaRecorder
    from av import AudioFrame
except ImportError:
    print("❌ Error: aiortc no está instalado. Ejecuta: pip install aiortc")
    sys.exit(1)

# =========================
# 📝 CONFIGURACIÓN DE LOGS
# =========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===========================================
# 🎛️ 1. PROCESADOR DE AUDIO (AudioProcessor)
# ===========================================


class AudioProcessor:
    """
    🔊 Procesador de audio en tiempo real.
    Convierte frames de audio en numpy arrays y extrae estadísticas útiles.
    """

    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.frame_count = 0
        self.total_audio_time = 0.0

    def process_audio_frame(self, frame: AudioFrame) -> Dict[str, Any]:
        """
        🧮 Procesa un frame de audio y retorna información del análisis.
        """
        try:
            # 🎲 Convertir frame a numpy array para análisis eficiente
            audio_array = frame.to_ndarray()

            # 📊 Estadísticas básicas
            rms = np.sqrt(np.mean(audio_array ** 2))  # Potencia del audio
            peak = np.max(np.abs(audio_array))        # Pico máximo

            # 🎼 Análisis de frecuencia (FFT)
            fft = np.fft.rfft(audio_array.flatten())
            freqs = np.fft.rfftfreq(
                len(audio_array.flatten()), 1/frame.sample_rate)
            dominant_freq_idx = np.argmax(np.abs(fft))
            dominant_freq = freqs[dominant_freq_idx]

            # 🗣️ Detección simple de voz (VAD)
            is_speech = rms > 0.01 and 80 <= dominant_freq <= 8000

            # ⏱️ Actualizar contadores
            self.frame_count += 1
            frame_duration = len(audio_array) / frame.sample_rate
            self.total_audio_time += frame_duration

            # 📦 Empaquetar resultados
            analysis = {
                'frame_number': self.frame_count,
                'timestamp': datetime.now().isoformat(),
                'duration_ms': frame_duration * 1000,
                'sample_rate': frame.sample_rate,
                'channels': frame.channels,
                'rms_level': float(rms),
                'peak_level': float(peak),
                'dominant_frequency': float(dominant_freq),
                'is_speech_detected': is_speech,
                'total_audio_time': self.total_audio_time,
                'audio_samples': len(audio_array)
            }

            logger.info(
                f"🎧 Audio procesado - Frame {self.frame_count}, RMS: {rms:.4f}, Peak: {peak:.4f}")
            return analysis

        except Exception as e:
            logger.error(f"❌ Error procesando audio: {e}")
            return {'error': str(e)}

# ==================================================
# 🎤 2. TRACK PERSONALIZADO PARA RECIBIR AUDIO (MediaStreamTrack)
# ==================================================


class AudioTrackReceiver(MediaStreamTrack):
    """
    🎤 Track personalizado para recibir y procesar audio.
    """
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.processor = AudioProcessor()
        self.websocket = None

    def set_websocket(self, websocket):
        """🔗 Asignar websocket para enviar resultados al cliente."""
        self.websocket = websocket

    async def recv(self):
        """📥 Recibe frames de audio, los procesa y envía resultados por WebSocket."""
        frame = await super().recv()
        if isinstance(frame, AudioFrame):
            analysis = self.processor.process_audio_frame(frame)
            if self.websocket and not self.websocket.closed:
                try:
                    await self.websocket.send(json.dumps({
                        'type': 'audio-processed',
                        'analysis': analysis,
                        'message': f"Frame {analysis.get('frame_number', 0)} procesado"
                    }))
                except Exception as e:
                    logger.error(f"❌ Error enviando análisis: {e}")
        return frame

# ==========================================
# 🌐 3. SERVIDOR WebRTC (WebRTCServer)
# ==========================================


class WebRTCServer:
    """
    🌐 Servidor WebRTC para audio en tiempo real.
    Maneja conexiones WebSocket y la lógica de señalización WebRTC.
    """

    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.peer_connections = set()
        self.audio_receivers = {}
        self.websocket_to_pc = {}  # Map websocket to RTCPeerConnection

    # 3.1. Manejo de conexiones WebSocket
    async def handle_websocket(self, websocket):
        """🔌 Maneja conexiones WebSocket entrantes."""
        client_address = websocket.remote_address
        logger.info(f"👤 Cliente conectado desde {client_address}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    logger.error("❌ Error decodificando mensaje JSON")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Formato de mensaje inválido'
                    }))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Cliente {client_address} desconectado")
        except Exception as e:
            logger.error(f"❌ Error en WebSocket: {e}")
        finally:
            await self.cleanup_connection(websocket)

    # 3.2. Procesamiento de mensajes WebSocket
    async def handle_message(self, websocket, data: Dict[str, Any]):
        """📨 Procesa mensajes del cliente."""
        message_type = data.get('type')
        if message_type == 'offer':
            await self.handle_offer(websocket, data)
        elif message_type == 'ice-candidate':
            await self.handle_ice_candidate(websocket, data)
        else:
            logger.warning(f"❓ Tipo de mensaje desconocido: {message_type}")

    # 3.3. Manejo de ofertas WebRTC
    async def handle_offer(self, websocket, data: Dict[str, Any]):
        """
        🤝 Maneja ofertas WebRTC, configura la conexión y los tracks de audio.
        """
        try:
            offer = RTCSessionDescription(
                sdp=data['offer']['sdp'],
                type=data['offer']['type']
            )
            pc = RTCPeerConnection()
            self.peer_connections.add(pc)
            self.websocket_to_pc[websocket] = pc  # Store mapping

            # 🎵 Cuando llega un track de audio, lo procesamos
            @pc.on("track")
            def on_track(track):
                logger.info(f"🎶 Track recibido: {track.kind}")
                if track.kind == "audio":
                    audio_receiver = AudioTrackReceiver()
                    audio_receiver.set_websocket(websocket)
                    self.audio_receivers[websocket] = audio_receiver
                    pc.addTrack(audio_receiver)
                    logger.info(
                        "🎤 Track de audio configurado para procesamiento")

            # 📡 Canal de datos opcional
            @pc.on("datachannel")
            def on_datachannel(channel):
                logger.info(f"📡 Canal de datos recibido: {channel.label}")

                @channel.on("message")
                def on_message(message):
                    try:
                        data = json.loads(message)
                        if data.get('type') == 'audio-config':
                            config = data.get('config', {})
                            logger.info(
                                f"⚙️ Configuración de audio recibida: {config}")
                    except json.JSONDecodeError:
                        logger.warning(
                            "❌ Mensaje de canal de datos no es JSON válido")

            # 🔄 Enviar ICE candidates generados por el servidor al cliente
            @pc.on("icecandidate")
            async def on_icecandidate(event):
                if event.candidate is not None:
                    try:
                        await websocket.send(json.dumps({
                            'type': 'ice-candidate',
                            'candidate': {
                                'candidate': event.candidate.candidate,
                                'sdpMid': event.candidate.sdpMid,
                                'sdpMLineIndex': event.candidate.sdpMLineIndex
                            }
                        }))
                        logger.info("➡️ ICE candidate enviado al cliente")
                    except Exception as e:
                        logger.error(f"❌ Error enviando ICE candidate: {e}")

            # 📝 Configurar la oferta y enviar respuesta (answer)
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await websocket.send(json.dumps({
                'type': 'answer',
                'answer': {
                    'sdp': pc.localDescription.sdp,
                    'type': pc.localDescription.type
                }
            }))
            logger.info("✅ Answer WebRTC enviado")

        except Exception as e:
            logger.error(f"❌ Error manejando offer: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Error procesando offer: {str(e)}'
            }))

    # 3.4. Manejo de ICE candidates
    async def handle_ice_candidate(self, websocket, data: Dict[str, Any]):
        """🧊 Maneja ICE candidates (conexión de red)."""
        try:
            logger.info("🧊 ICE candidate recibido")
            candidate = data.get('candidate')
            if not candidate:
                logger.warning("❌ ICE candidate vacío")
                return
            pc = self.websocket_to_pc.get(websocket)
            if not pc:
                logger.warning("❌ No se encontró RTCPeerConnection para este websocket")
                return
            # Pasa el dict candidate directamente a addIceCandidate
            await pc.addIceCandidate(candidate)
            logger.info("✅ ICE candidate añadido a RTCPeerConnection")
        except Exception as e:
            logger.error(f"❌ Error manejando ICE candidate: {e}")

    # 3.5. Limpieza de recursos al cerrar conexión
    async def cleanup_connection(self, websocket):
        """🧹 Limpia recursos cuando se cierra una conexión."""
        try:
            connections_to_remove = []
            for pc in self.peer_connections:
                try:
                    await pc.close()
                    connections_to_remove.append(pc)
                except:
                    pass
            for pc in connections_to_remove:
                self.peer_connections.discard(pc)
            if websocket in self.audio_receivers:
                del self.audio_receivers[websocket]
            if websocket in self.websocket_to_pc:
                del self.websocket_to_pc[websocket]
            logger.info("🧹 Recursos de conexión limpiados")
        except Exception as e:
            logger.error(f"❌ Error limpiando conexión: {e}")

    # 3.6. Iniciar el servidor WebSocket
    async def start_server(self):
        """🚀 Inicia el servidor WebRTC y escucha conexiones."""
        logger.info(f"🚦 Iniciando servidor WebRTC en {self.host}:{self.port}")

        # Manejo de señales para cierre limpio
        def signal_handler(signum, frame):
            logger.info("🛑 Señal de cierre recibida, cerrando servidor...")
            asyncio.create_task(self.stop_server())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        handler = functools.partial(self.handle_websocket)

        # Configurar SSL si hay certificados
        ssl_context = None
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile="../web/cert.pem", keyfile="../web/key.pem")
            logger.info("🔒 Servidor WebSocket seguro (WSS) habilitado.")
        except Exception as e:
            logger.warning(f"No se pudo cargar SSL: {e}. El servidor funcionará en modo no seguro (WS)")
            ssl_context = None

        async with websockets.serve(
            handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10,
            ssl=ssl_context
        ):
            logger.info(
                f"🌐 Servidor WebRTC ejecutándose en ws{'s' if ssl_context else ''}://{self.host}:{self.port}")
            logger.info("💡 Presiona Ctrl+C para detener el servidor")
            await asyncio.Future()  # Mantener el servidor corriendo

    # 3.7. Detener el servidor y limpiar recursos
    async def stop_server(self):
        """🛑 Detiene el servidor y limpia recursos."""
        logger.info("🛑 Deteniendo servidor...")
        for pc in self.peer_connections.copy():
            try:
                await pc.close()
            except:
                pass
        self.peer_connections.clear()
        self.audio_receivers.clear()
        logger.info("✅ Servidor detenido")

# =========================
# 🏁 PUNTO DE ENTRADA MAIN
# =========================


def main():
    """🏁 Función principal para iniciar el servidor."""
    try:
        server = WebRTCServer()
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
