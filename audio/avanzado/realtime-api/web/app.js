// 🎤 Realtime API (modo simple)
// Objetivo: el mínimo código posible para entender la demo, con comentarios didácticos.
// Flujo: 🎙️ micrófono -> 📡 WebRTC -> 🤖 OpenAI Realtime -> 🔊 audio + 💬 texto

(function () {
    const state = {
        pc: null,
        dc: null,
        audioEl: null,
        connected: false,
        ephemeralKey: null,
        model: 'gpt-4o-realtime-preview-2024-12-17'
    };

    // 🔖 Flags simples para mostrar estados de envío/recepción sin duplicar mensajes
    let receivingText = false;
    let receivingAudio = false;
    let sendingAudio = false;

    // UI
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    // UI de texto eliminada: audio-only
    const messages = document.getElementById('messages');
        const micBadge = document.getElementById('micBadge');
        const sendingBadge = document.getElementById('sendingBadge');
        const receivingBadge = document.getElementById('receivingBadge');

    // 🔄 Actualiza la interfaz según el estado de conexión
    function setConnected(on) {
        state.connected = on;
        statusDot.classList.toggle('on', on);
        statusText.textContent = on ? 'Conectado' : 'Desconectado';
        connectBtn.disabled = on;
        disconnectBtn.disabled = !on;
    // sin campos de texto en modo audio-only
            if(!on){
                // Reset visual badges al desconectar
                micBadge.classList.add('hidden');
                sendingBadge.classList.add('hidden');
                receivingBadge.classList.add('hidden');
            }
    }

    // 💬 Pinta un mensaje sencillo en el chat (quién: 'user' | 'assistant')
    function addMsg(text, who) {
        const row = document.createElement('div');
        row.className = who; // 'user' | 'assistant'
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        row.appendChild(bubble);
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
    }

    // 🧭 Mensajes de estado del sistema (centrados y discretos)
    function addSystem(text) {
        const row = document.createElement('div');
        row.className = 'system';
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        row.appendChild(bubble);
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
    }

    // 🔐 Pide al servidor Python una "ephemeral key" para autenticarnos frente a OpenAI
    // Ventaja: nunca exponemos nuestra API key en el navegador (seguridad) 🔒
    async function getEphemeralKey() {
        // servidor Python corre en el mismo puerto/host; token en /api/token
        const base = `${location.protocol}//${location.host}`;
        const res = await fetch(`${base}/api/token`, { method: 'POST' });
        if (!res.ok) throw new Error(`Token HTTP ${res.status}`);
        const data = await res.json();
        const key = data?.client_secret?.value;
        if (!key) throw new Error('Token no recibido');
        return key;
    }

    // 🚀 Arranca una sesión Realtime de extremo a extremo
    // Pasos:
    // 1) Obtener token efímero 🔐
    // 2) Crear RTCPeerConnection 📡 y un <audio> para reproducir respuestas 🔊
    // 3) Pedir permiso al micrófono y adjuntar el track 🎙️
    // 4) Crear dataChannel para eventos JSON 📨
    // 5) Intercambiar SDP con OpenAI (offer/answer) 🤝
    async function start() {
        try {
            setConnected(false);
            addSystem('🔌 Conectando...');
            // 1) Token efímero
            state.ephemeralKey = await getEphemeralKey();
            addSystem('🔑 Token efímero obtenido');

            // 2) PeerConnection y <audio>
            state.pc = new RTCPeerConnection();
            state.audioEl = new Audio();
            state.audioEl.autoplay = true;
            // Cuando OpenAI nos envía audio por WebRTC, lo reproducimos automáticamente
            state.pc.ontrack = (e) => { state.audioEl.srcObject = e.streams[0]; };

            // 3) micrófono
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 }
            });
            const track = stream.getAudioTracks()[0];
            state.pc.addTrack(track);

            // 4) Data channel
            state.dc = state.pc.createDataChannel('oai-events');
            // Al abrir el canal, enviamos una configuración mínima de sesión
            state.dc.onopen = () => {
                setConnected(true);
                addSystem('📡 Canal de datos abierto');
                // Configuración mínima: voz e instrucciones + transcripción
                sendEvent({
                    type: 'session.update',
                    session: {
                        instructions: 'Eres un asistente útil y conciso en español.',
                        voice: 'verse',
                        input_audio_format: 'pcm16',
                        output_audio_format: 'pcm16',
                        input_audio_transcription: { model: 'whisper-1' }
                    }
                });
            };
            // Todos los mensajes del modelo llegan por aquí como eventos JSON
            state.dc.onmessage = (ev) => handleServerEvent(JSON.parse(ev.data));

            // 5) SDP: offer -> POST a OpenAI -> answer
            const offer = await state.pc.createOffer();
            await state.pc.setLocalDescription(offer);
            addSystem('📨 Enviando oferta SDP a OpenAI');
            const url = `https://api.openai.com/v1/realtime?model=${encodeURIComponent(state.model)}`;
            const resp = await fetch(url, {
                method: 'POST',
                headers: { Authorization: `Bearer ${state.ephemeralKey}`, 'Content-Type': 'application/sdp' },
                body: offer.sdp
            });
            if (!resp.ok) throw new Error(`OpenAI HTTP ${resp.status}`);
            const answerSdp = await resp.text();
            await state.pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });
            addSystem('✅ Conectado con OpenAI (answer SDP recibida)');

        } catch (err) {
            console.error(err);
            addMsg('⚠️ Error al conectar. Revisa la consola.', 'assistant');
            addSystem('❌ Error en la conexión');
            await stop();
        }
    }

    // 🧹 Detiene la sesión y libera recursos (micrófono, peer, audio)
    async function stop() {
        try {
            if (state.dc) { try { state.dc.close(); } catch { } state.dc = null; }
            if (state.pc) {
                try {
                    state.pc.getSenders().forEach(s => s.track && s.track.stop());
                } catch { }
                try { state.pc.close(); } catch { }
                state.pc = null;
            }
            if (state.audioEl) { state.audioEl.pause(); state.audioEl.srcObject = null; state.audioEl = null; }
        } finally {
            setConnected(false);
        }
    }

    // 📨 Envía un evento JSON al modelo por el dataChannel
    function sendEvent(obj) {
        if (!state.dc || state.dc.readyState !== 'open') return;
        state.dc.send(JSON.stringify(obj));
    }

    // 📥 Procesa los eventos que envía OpenAI
    function handleServerEvent(ev) {
        switch (ev.type) {
            case 'session.created':
                addMsg('✅ Sesión creada. Puedes hablar.', 'assistant'); // Confirmación
                addSystem('🟢 Sesión lista');
                break;
            case 'input_audio_buffer.speech_started':
                // Usuario empezó a hablar: estamos capturando y enviando audio
                currentAssistantRow = null; // empezar nueva burbuja de respuesta
                receivingText = false;
                receivingAudio = false;
                sendingAudio = true;
                    // Badges
                    micBadge.textContent = '🎙️ Escuchando';
                    micBadge.classList.remove('hidden');
                    sendingBadge.classList.remove('hidden');
                    receivingBadge.classList.add('hidden');
                addSystem('🎙️ Hablando…');
                addSystem('📤 Enviando audio a OpenAI…');
                break;
            case 'input_audio_buffer.speech_stopped':
                    micBadge.textContent = '⏳ Procesando';
                addSystem('🛑 Fin del audio');
                break;
            case 'input_audio_buffer.committed':
                // OpenAI confirma que recibió el buffer de audio
                sendingAudio = false;
                    sendingBadge.classList.add('hidden');
                addSystem('📤 Audio enviado a OpenAI');
                break;
            case 'input_audio_buffer.transcription_completed':
                // Transcripción final de lo que dijo el usuario 🎙️➡️📝
                if (ev.transcript) {
                    addSystem('📝 Transcripción completada');
                    addMsg(ev.transcript, 'user');
                    addSystem('🤖 Generando respuesta...');
                }
                break;
            case 'response.text.delta':
                // Texto del asistente en streaming: vamos agregando trocitos 💬⏳
                if (ev.delta) {
                    if (!receivingText) {
                        receivingText = true;
                            // Mostrar badge de recepción
                            receivingBadge.classList.remove('hidden');
                        addSystem('📥 Recibiendo texto de OpenAI…');
                    }
                    appendAssistantDelta(ev.delta);
                }
                break;
            case 'response.audio.delta':
                // Audio del asistente en streaming (aunque no lo transcribimos aquí)
                if (!receivingAudio) {
                    receivingAudio = true;
                        receivingBadge.classList.remove('hidden');
                    addSystem('📥 Recibiendo audio de OpenAI…');
                }
                break;
            case 'response.audio.done':
                    // Si no hay más streams entrantes, ocultar badge de recepción
                    receivingBadge.classList.add('hidden');
                    micBadge.classList.add('hidden');
                addSystem('✅ Audio completo recibido');
                break;
            case 'response.text.done':
                // Fin del texto actual (no necesitamos acción extra en modo simple)
                    receivingBadge.classList.add('hidden');
                    micBadge.classList.add('hidden');
                addSystem('✅ Respuesta recibida');
                break;
            default:
                // Para mantenerlo simple, ignoramos otros eventos aquí
                break;
        }
    }

    // 🧱 Construye el mensaje del asistente de forma progresiva
    let currentAssistantRow = null;
    function appendAssistantDelta(text) {
        if (!currentAssistantRow) {
            currentAssistantRow = document.createElement('div');
            currentAssistantRow.className = 'assistant';
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            currentAssistantRow.appendChild(bubble);
            messages.appendChild(currentAssistantRow);
        }
        const bubble = currentAssistantRow.querySelector('.bubble');
        bubble.textContent += text;
        messages.scrollTop = messages.scrollHeight;
    }

    // 🔗 Conectar eventos de la UI
    connectBtn.addEventListener('click', start);
    disconnectBtn.addEventListener('click', stop);
})();
