// visualizer.js
// Animación de onda para el reproductor de audio

export function setupAudioVisualizer(audioElement, canvasElement) {
  const ctx = canvasElement.getContext('2d');
  let audioCtx, analyser, source, dataArray, animationId;

  function resizeCanvas() {
    canvasElement.width = canvasElement.offsetWidth;
    canvasElement.height = 80;
  }

  function draw() {
    if (!analyser) return;
    analyser.getByteTimeDomainData(dataArray);
    ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#00e0ff';
    ctx.beginPath();
    const sliceWidth = canvasElement.width / dataArray.length;
    let x = 0;
    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvasElement.height) / 2;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }
    ctx.lineTo(canvasElement.width, canvasElement.height / 2);
    ctx.stroke();
    animationId = requestAnimationFrame(draw);
  }

  function start() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioCtx.createAnalyser();
      source = audioCtx.createMediaElementSource(audioElement);
      source.connect(analyser);
      analyser.connect(audioCtx.destination);
      analyser.fftSize = 2048;
      dataArray = new Uint8Array(analyser.fftSize);
    }
    draw();
  }

  function stop() {
    if (animationId) cancelAnimationFrame(animationId);
    ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  }

  audioElement.addEventListener('play', start);
  audioElement.addEventListener('pause', stop);
  audioElement.addEventListener('ended', stop);
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();
}
