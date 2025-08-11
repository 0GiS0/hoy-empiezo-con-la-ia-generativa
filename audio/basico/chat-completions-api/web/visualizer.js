// RAP Audio Visualizer
// Static, clean visualization for hip-hop beats

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
            
            console.log('🎤 RAP Visualizer initialized');
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
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Configurar estilos
        const barWidth = (canvasElement.width / dataArray.length) * 2.5;
        let barHeight;
        let x = 0;
        
        // Dibujar barras del visualizador
        for (let i = 0; i < dataArray.length; i++) {
            barHeight = (dataArray[i] / 255) * canvasElement.height * 0.8;
            
            // Colores RAP: oro y rojo
            const intensity = dataArray[i] / 255;
            if (intensity > 0.7) {
                ctx.fillStyle = '#ffd700'; // Oro para frecuencias altas
            } else if (intensity > 0.4) {
                ctx.fillStyle = '#ff4444'; // Rojo para frecuencias medias
            } else {
                ctx.fillStyle = '#666'; // Gris para frecuencias bajas
            }
            
            ctx.fillRect(x, canvasElement.height - barHeight, barWidth, barHeight);
            
            x += barWidth + 1;
        }
    }

    // Función para mostrar visualización estática
    function drawStaticVisualization() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Dibujar barras estáticas
        const barCount = 32;
        const barWidth = canvasElement.width / barCount;
        
        for (let i = 0; i < barCount; i++) {
            const barHeight = Math.random() * canvasElement.height * 0.3 + 10;
            const x = i * barWidth;
            
            ctx.fillStyle = '#333';
            ctx.fillRect(x, canvasElement.height - barHeight, barWidth - 2, barHeight);
        }
        
        // Texto central
        ctx.fillStyle = '#ffd700';
        ctx.font = 'bold 16px Impact';
        ctx.textAlign = 'center';
        ctx.fillText('🎤 RAP VISUALIZER 🎵', canvasElement.width / 2, canvasElement.height / 2);
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
        console.log('🎵 RAP beat started');
    });

    audioElement.addEventListener('pause', () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        console.log('⏸️ Beat paused');
    });

    audioElement.addEventListener('ended', () => {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        drawStaticVisualization();
        console.log('🔚 Beat finished');
    });

    // Inicializar con visualización estática
    drawStaticVisualization();
}
