// 🎤 Chat Completions (modo simple, estética unificada con Realtime)
(function(){
    const API_BASE = `${location.protocol}//${location.host}`; // mismo host/puerto

    // Estado mínimo
    const state = {
        isRecording: false,
        mediaRecorder: null,
        chunks: [],
        stream: null,
        currentAudio: null,
        timerStart: null
    };

    // UI refs
    const recordBtn = document.getElementById('recordBtn');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const micBadge = document.getElementById('micBadge');
    const sendingBadge = document.getElementById('sendingBadge');
    const receivingBadge = document.getElementById('receivingBadge');
    const messages = document.getElementById('messages');

    function setRecording(on){
        state.isRecording = on;
        statusDot.classList.toggle('on', on);
        statusText.textContent = on ? 'Grabando' : 'Listo';
        recordBtn.textContent = on ? 'Soltar para enviar' : 'Grabar';
        micBadge.textContent = on ? '🎙️ Escuchando' : '';
        micBadge.classList.toggle('hidden', !on);
    }

    function addMsg(text, who){
        const row = document.createElement('div');
        row.className = who; // 'user' | 'assistant'
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        row.appendChild(bubble);
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
    }

    function addSystem(text){
        const row = document.createElement('div');
        row.className = 'system';
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        row.appendChild(bubble);
        messages.appendChild(row);
        messages.scrollTop = messages.scrollHeight;
    }

    async function start(){
        if(state.isRecording) return;
        try{
            state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            state.chunks = [];
            state.mediaRecorder = new MediaRecorder(state.stream);
            state.mediaRecorder.ondataavailable = (e)=>{ if(e.data.size>0) state.chunks.push(e.data); };
            state.mediaRecorder.onstop = onStop;
            state.mediaRecorder.start();
            setRecording(true);
            addSystem('🎙️ Hablando…');
        }catch(err){
            console.error(err);
            addSystem('❌ Error accediendo al micrófono');
        }
    }

    function stop(){
        if(!state.isRecording) return;
        state.mediaRecorder.stop();
        setRecording(false);
        micBadge.textContent = '⏳ Procesando';
        micBadge.classList.remove('hidden');
        state.timerStart = (typeof performance!=='undefined'? performance.now(): Date.now());
    }

    async function onStop(){
        try{
            // liberar el track
            try { state.stream.getTracks().forEach(t=>t.stop()); } catch {}
            const blob = new Blob(state.chunks, { type: 'audio/wav' });

            sendingBadge.classList.remove('hidden');
            addSystem('📤 Enviando audio al servidor…');

            const fd = new FormData();
            fd.append('audio', blob, 'recording.wav');
            const resp = await fetch(`${API_BASE}/conversation`, { method:'POST', body: fd });
            if(!resp.ok) throw new Error(`HTTP ${resp.status}`);

            receivingBadge.classList.remove('hidden');
            sendingBadge.classList.add('hidden');
            addMsg('🎤 Audio enviado', 'user');
            addSystem('🤖 Generando respuesta…');

            const buf = await resp.arrayBuffer();
            const outBlob = new Blob([buf], { type: 'audio/wav' });
            const url = URL.createObjectURL(outBlob);

            // tiempo
            let pretty = null;
            if(state.timerStart){
                const end = (typeof performance!=='undefined'? performance.now(): Date.now());
                const secs = (end - state.timerStart)/1000;
                pretty = secs < 10 ? `${secs.toFixed(1)} s` : `${Math.round(secs)} s`;
            }

            // reproducir
            try { if(state.currentAudio){ state.currentAudio.pause(); state.currentAudio=null; } } catch{}
            const audio = new Audio(url);
            state.currentAudio = audio;
            audio.onended = ()=>{ state.currentAudio=null; receivingBadge.classList.add('hidden'); micBadge.classList.add('hidden'); };
            await audio.play();

            addMsg(pretty ? `🔊 Respuesta recibida (${pretty})` : '🔊 Respuesta recibida', 'assistant');
            state.timerStart = null;
        }catch(err){
            console.error(err);
            sendingBadge.classList.add('hidden');
            receivingBadge.classList.add('hidden');
            micBadge.classList.add('hidden');
            addSystem('❌ Error procesando la conversación');
        }
    }

    // Eventos UI
    recordBtn.addEventListener('mousedown', start);
    recordBtn.addEventListener('mouseup', stop);
    recordBtn.addEventListener('mouseleave', ()=>{ if(state.isRecording) stop(); });
    document.addEventListener('keydown', (e)=>{ if(e.code==='Space' && !state.isRecording){ e.preventDefault(); start(); }});
    document.addEventListener('keyup', (e)=>{ if(e.code==='Space' && state.isRecording){ e.preventDefault(); stop(); }});
})();

