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
    
    console.log('🎤 RAP Generator AI initialized successfully!');
}

// Handle form submission
async function handleFormSubmission(e) {
    e.preventDefault();
    
    // Update UI for loading state
    updateUIForLoading();
    
    const message = document.getElementById('message').value;
    const selectedVoice = document.querySelector('input[name="voice"]:checked');
    const voice = selectedVoice ? selectedVoice.value : 'echo';

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
    const response = await fetch('http://127.0.0.1:5000/generate-audio', {
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
