import { setupAudioVisualizer } from './visualizer.js';

// DOM elements
const form = document.getElementById('audioForm');
const audioPlayer = document.getElementById('audioPlayer');
const statusDiv = document.getElementById('status');
const visualizer = document.getElementById('visualizer');
const generateBtn = document.getElementById('generateBtn');
const audioContainer = document.getElementById('audioContainer');

// Initialize the application
function initApp() {
    // Setup audio visualizer
    setupAudioVisualizer(audioPlayer, visualizer);
    
    // Setup form submission handler
    form.addEventListener('submit', handleFormSubmission);
    
    // Setup voice selection listeners
    const voiceInputs = document.querySelectorAll('input[name="voice"]');
    voiceInputs.forEach(input => {
        input.addEventListener('change', function() {
            console.log('🎭 Cambio de voz detectado:', this.value);
            // Update UI to show selected voice
            updateVoiceSelection(this.value);
        });
    });
    
    // Ensure a voice is selected (fallback to echo if none selected)
    ensureVoiceSelected();
    
    console.log('🎤 RAP Generator AI initialized successfully!');
}

// Ensure a voice is selected, default to 'echo' if none
function ensureVoiceSelected() {
    const selectedVoice = document.querySelector('input[name="voice"]:checked');
    
    if (!selectedVoice) {
        const echoVoice = document.getElementById('echo');
        if (echoVoice) {
            echoVoice.checked = true;
            console.log('🎭 Voz por defecto establecida: echo');
        } else {
            // If echo doesn't exist, select the first available voice
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

// Handle form submission
async function handleFormSubmission(e) {
    e.preventDefault();
    
    // Update UI for loading state
    updateUIForLoading();
    
    const message = document.getElementById('message').value;
    
    // Ensure a voice is selected before processing
    ensureVoiceSelected();
    
    // Debug: Log all radio buttons
    const allVoiceInputs = document.querySelectorAll('input[name="voice"]');
    console.log('🎙️ Todas las voces encontradas:', allVoiceInputs.length);
    
    allVoiceInputs.forEach(input => {
        console.log(`🎵 Voz: ${input.value}, Checked: ${input.checked}`);
    });
    
    // Get selected voice with better detection
    const selectedVoice = document.querySelector('input[name="voice"]:checked');
    console.log('🎤 Voz seleccionada:', selectedVoice);
    
    // More robust voice selection with fallback
    let voice = 'echo'; // Default fallback
    if (selectedVoice && selectedVoice.value) {
        voice = selectedVoice.value;
    } else {
        console.warn('⚠️ No se encontró voz seleccionada, usando fallback:', voice);
        // Try to select echo as fallback
        const echoInput = document.getElementById('echo');
        if (echoInput) {
            echoInput.checked = true;
        }
    }
    
    console.log('🔥 Voz final enviada a la API:', voice);

    try {
        const audioBlob = await generateAudio(message, voice);
        await playGeneratedAudio(audioBlob);
        updateUIForSuccess();
    } catch (error) {
        updateUIForError(error);
    } finally {
        resetGenerateButton();
    }
}

// Generate audio from the API
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

// Play the generated audio
async function playGeneratedAudio(blob) {
    const url = URL.createObjectURL(blob);
    audioPlayer.src = url;
    
    // Show audio controls
    audioContainer.style.display = 'block';
    
    await audioPlayer.play();
}

// UI Update functions
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

// Update voice selection feedback
function updateVoiceSelection(selectedVoice) {
    console.log('🎭 Voz actualizada a:', selectedVoice);
    
    // You can add visual feedback here if needed
    // For example, updating a status message
    const currentStatus = document.getElementById('status');
    if (currentStatus && !currentStatus.innerHTML.includes('COOKING') && !currentStatus.innerHTML.includes('ERROR')) {
        const placeholder = currentStatus.querySelector('.placeholder div:last-child');
        if (placeholder) {
            placeholder.textContent = `LISTO PARA SOLTAR FUEGO CON ${selectedVoice.toUpperCase()}`;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
