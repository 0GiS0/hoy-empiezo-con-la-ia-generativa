
/*
-------------------------------------------------------------
🎤 RAP Generator AI - Interfaz Web

Este archivo gestiona la interacción del usuario para generar raps con IA.
Flujo principal:
1️⃣ El usuario escribe un mensaje y selecciona una voz.
2️⃣ Al enviar el formulario, se llama a la API para generar el audio.
3️⃣ Se reproduce el audio generado y se visualiza el beat.
4️⃣ Los estados y mensajes se actualizan dinámicamente.

Todos los comentarios están en español y con emojis para que sea fácil de seguir y didáctico.
-------------------------------------------------------------
*/

import { setupAudioVisualizer } from './visualizer.js';

// 🎚️ Elementos del DOM
const form = document.getElementById('audioForm');
const audioPlayer = document.getElementById('audioPlayer');
const statusDiv = document.getElementById('status');
const visualizer = document.getElementById('visualizer');
const generateBtn = document.getElementById('generateBtn');
const audioContainer = document.getElementById('audioContainer');

// 🚀 Inicializa la aplicación y los listeners
function initApp() {
    // 🎵 Inicializa el visualizador de audio
    setupAudioVisualizer(audioPlayer, visualizer);

    // 📨 Listener para el envío del formulario
    form.addEventListener('submit', handleFormSubmission);

    // 🎭 Listener para el cambio de voz
    const voiceInputs = document.querySelectorAll('input[name="voice"]');
    voiceInputs.forEach(input => {
        input.addEventListener('change', function() {
            console.log('🎭 Cambio de voz detectado:', this.value);
            // Actualiza la UI para mostrar la voz seleccionada
            updateVoiceSelection(this.value);
        });
    });

    // 🛡️ Asegura que haya una voz seleccionada (por defecto 'echo')
    ensureVoiceSelected();

    console.log('🎤 RAP Generator AI inicializado correctamente!');
}

// 🛡️ Asegura que haya una voz seleccionada, por defecto 'echo'
function ensureVoiceSelected() {
    const selectedVoice = document.querySelector('input[name="voice"]:checked');

    if (!selectedVoice) {
        const echoVoice = document.getElementById('echo');
        if (echoVoice) {
            echoVoice.checked = true;
            console.log('🎭 Voz por defecto establecida: echo');
        } else {
            // Si no existe 'echo', selecciona la primera voz disponible
            const firstVoice = document.querySelector('input[name="voice"]');
            if (firstVoice) {
                firstVoice.checked = true;
                console.log('🎭 Primera voz disponible seleccionada:', firstVoice.value);
            }
        }
    } else {
        console.log('🎭 Voz ya seleccionada:', selectedVoice.value);
    }
}

// 📨 Maneja el envío del formulario para generar el rap
async function handleFormSubmission(e) {
    e.preventDefault();

    // ⏳ Actualiza la UI para mostrar estado de carga
    updateUIForLoading();

    const message = document.getElementById('message').value;

    // 🛡️ Asegura que haya una voz seleccionada antes de procesar
    ensureVoiceSelected();

    // 🕵️‍♂️ Debug: Muestra todas las voces disponibles
    const allVoiceInputs = document.querySelectorAll('input[name="voice"]');
    console.log('🎙️ Todas las voces encontradas:', allVoiceInputs.length);
    allVoiceInputs.forEach(input => {
        console.log(`🎵 Voz: ${input.value}, Checked: ${input.checked}`);
    });

    // 🎤 Obtiene la voz seleccionada, con fallback
    const selectedVoice = document.querySelector('input[name="voice"]:checked');
    console.log('🎤 Voz seleccionada:', selectedVoice);

    let voice = 'echo'; // Fallback por defecto
    if (selectedVoice && selectedVoice.value) {
        voice = selectedVoice.value;
    } else {
        console.warn('⚠️ No se encontró voz seleccionada, usando fallback:', voice);
        // Intenta seleccionar 'echo' como fallback
        const echoInput = document.getElementById('echo');
        if (echoInput) {
            echoInput.checked = true;
        }
    }

    console.log('🔥 Voz final enviada a la API:', voice);

    try {
        // 🛠️ Llama a la API para generar el audio
        const audioBlob = await generateAudio(message, voice);
        // 🔊 Reproduce el audio generado
        await playGeneratedAudio(audioBlob);
        // 🎉 Actualiza la UI para mostrar éxito
        updateUIForSuccess();
    } catch (error) {
        // ⚠️ Muestra error en la UI
        updateUIForError(error);
    } finally {
        // 🔄 Restablece el botón de generar
        resetGenerateButton();
    }
}

// 🛠️ Llama a la API para generar el audio
async function generateAudio(message, voice) {
    const response = await fetch('http://localhost:5001/generate-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, voice })
    });

    if (!response.ok) {
        throw new Error('🔥 Error en el beat');
    }

    return await response.blob();
}

// 🔊 Reproduce el audio generado
async function playGeneratedAudio(blob) {
    const url = URL.createObjectURL(blob);
    audioPlayer.src = url;

    // 🎚️ Muestra los controles de audio
    audioContainer.style.display = 'block';

    await audioPlayer.play();
}

// 🖥️ Funciones para actualizar la UI
function updateUIForLoading() {
    generateBtn.disabled = true;
    generateBtn.innerHTML = '⏳ COOKING THE BEAT...';
    audioContainer.style.display = 'none';
    statusDiv.innerHTML = '<div class="loading"></div> 🎵 CREANDO TU RAP CON IA...';
}

function updateUIForSuccess() {
    statusDiv.innerHTML = '🔥 ¡BEAT READY! EL RAP ESTÁ ON FIRE 🎤';
}

function updateUIForError(error) {
    statusDiv.innerHTML = '⚠️ ERROR EN EL STUDIO: ' + error.message + ' 🔧';
}

function resetGenerateButton() {
    generateBtn.disabled = false;
    generateBtn.innerHTML = '🎬 DROP THE BEAT! 🎵';
}

// 🎭 Actualiza el feedback visual al cambiar la voz
function updateVoiceSelection(selectedVoice) {
    console.log('🎭 Voz actualizada a:', selectedVoice);

    // Puedes añadir feedback visual aquí si lo necesitas
    // Por ejemplo, actualizar un mensaje de estado
    const currentStatus = document.getElementById('status');
    if (currentStatus && !currentStatus.innerHTML.includes('COOKING') && !currentStatus.innerHTML.includes('ERROR')) {
        const placeholder = currentStatus.querySelector('.placeholder div:last-child');
        if (placeholder) {
            placeholder.textContent = `LISTO PARA SOLTAR FUEGO CON ${selectedVoice.toUpperCase()}`;
        }
    }
}

// 🚦 Inicializa la app cuando el DOM está listo
document.addEventListener('DOMContentLoaded', initApp);
