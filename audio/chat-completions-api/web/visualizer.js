// visualizer.js
// Animación de onda para el reproductor de audio

export function setupAudioVisualizer(audioElement, canvasElement) {
    if (!audioElement || !canvasElement) {
        console.warn('⚠️ Audio element o canvas element no encontrados');
        return;
    }

    const ctx = canvasElement.getContext('2d');
    let audioContext;
    let analyser;
    let dataArray;
    let animationId;

    // Configurar el contexto de audio
    function initAudioContext() {
        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            
            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
            
            const source = audioContext.createMediaElementSource(audioElement);
            source.connect(analyser);
            analyser.connect(audioContext.destination);
            
            console.log('🎵 Visualizador de audio inicializado correctamente');
        } catch (error) {
            console.error('❌ Error inicializando audio context:', error);
        }
    }

    // Función de dibujo del visualizador
    function draw() {
        if (!analyser || !dataArray) return;
        
        animationId = requestAnimationFrame(draw);
        
        analyser.getByteFrequencyData(dataArray);
        
        // Limpiar canvas
        ctx.fillStyle = 'rgba(26, 26, 46, 0.8)';
        ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Configurar estilos
        const barWidth = (canvasElement.width / dataArray.length) * 2.5;
        let barHeight;
        let x = 0;
        
        // Dibujar barras del visualizador
        for (let i = 0; i < dataArray.length; i++) {
            barHeight = (dataArray[i] / 255) * canvasElement.height * 0.8;
            
            // Gradiente para las barras
            const gradient = ctx.createLinearGradient(0, canvasElement.height - barHeight, 0, canvasElement.height);
            gradient.addColorStop(0, '#4ecdc4');
            gradient.addColorStop(0.5, '#45b7d1');
            gradient.addColorStop(1, '#ff6b6b');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, canvasElement.height - barHeight, barWidth, barHeight);
            
            // Efecto de brillo en la parte superior
            ctx.fillStyle = 'rgba(78, 205, 196, 0.8)';
            ctx.fillRect(x, canvasElement.height - barHeight, barWidth, 2);
            
            x += barWidth + 1;
        }
        
        // Agregar ondas de fondo
        drawBackgroundWaves();
    }

    // Dibujar ondas de fondo decorativas
    function drawBackgroundWaves() {
        const time = Date.now() * 0.001;
        
        ctx.strokeStyle = 'rgba(78, 205, 196, 0.3)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        for (let x = 0; x < canvasElement.width; x += 5) {
            const y = canvasElement.height * 0.5 + Math.sin((x * 0.01) + time) * 20;
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        
        ctx.stroke();
        
        // Segunda onda
        ctx.strokeStyle = 'rgba(255, 107, 107, 0.2)';
        ctx.beginPath();
        
        for (let x = 0; x < canvasElement.width; x += 5) {
            const y = canvasElement.height * 0.3 + Math.sin((x * 0.02) + time * 1.5) * 15;
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        
        ctx.stroke();
    }

    // Función para mostrar visualización estática
    function drawStaticVisualization() {
        ctx.fillStyle = 'rgba(26, 26, 46, 0.9)';
        ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Dibujar barras estáticas
        const barCount = 32;
        const barWidth = canvasElement.width / barCount;
        
        for (let i = 0; i < barCount; i++) {
            const barHeight = Math.random() * canvasElement.height * 0.3 + 10;
            const x = i * barWidth;
            
            const gradient = ctx.createLinearGradient(0, canvasElement.height - barHeight, 0, canvasElement.height);
            gradient.addColorStop(0, 'rgba(78, 205, 196, 0.3)');
            gradient.addColorStop(1, 'rgba(78, 205, 196, 0.6)');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(x, canvasElement.height - barHeight, barWidth - 2, barHeight);
        }
        
        // Texto central
        ctx.fillStyle = 'rgba(78, 205, 196, 0.8)';
        ctx.font = '16px Courier New';
        ctx.textAlign = 'center';
        ctx.fillText('🎵 RADIO AI VISUALIZER 🎵', canvasElement.width / 2, canvasElement.height / 2);
        
        drawBackgroundWaves();
    }

    // Event listeners
    audioElement.addEventListener('play', () => {
        if (!audioContext) {
            initAudioContext();
        }
        if (audioContext && audioContext.state === 'suspended') {
            audioContext.resume();
        }
        draw();
        console.log('🎵 Iniciando visualizador');
    });

    audioElement.addEventListener('pause', () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        console.log('⏸️ Visualizador pausado');
    });

    audioElement.addEventListener('ended', () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        drawStaticVisualization();
        console.log('🔚 Audio terminado');
    });

    // Inicializar con visualización estática
    drawStaticVisualization();
    
    // Animar las ondas de fondo incluso sin audio
    function animateBackground() {
        if (!audioElement.paused) return; // Solo animar cuando no hay audio
        
        drawStaticVisualization();
        requestAnimationFrame(animateBackground);
    }
    
    animateBackground();
}
