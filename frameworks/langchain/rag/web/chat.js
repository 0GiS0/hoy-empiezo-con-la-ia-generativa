// URL del endpoint del backend, obtenida dinámicamente por si cambia el puerto.
const API_URL = document.location.origin + '/chat';

// Elementos del DOM
const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('input');
const statusEl = document.getElementById('status');

// Generar / recuperar un sessionId persistente para simular usuarios distintos
function getSessionId() {
  const KEY = 'chat_session_id';
  let id = localStorage.getItem(KEY);
  if (!id) {
    // ID sencillo: fecha base36 + 8 chars aleatorios
    const rand = Math.random().toString(36).slice(2, 10);
    id = Date.now().toString(36) + '-' + rand;
    localStorage.setItem(KEY, id);
  }
  return id;
}

// Generar o recuperar un ID de sesión único
const SESSION_ID = getSessionId();

// Permite añadir un mensaje al chat
function appendMessage(role, content, references = null) {
  const tpl = document.getElementById('message-template');
  const node = tpl.content.firstElementChild.cloneNode(true);
  node.classList.add(role === 'user' ? 'user' : 'assistant');
  node.querySelector('[data-role="avatar"]').textContent = role === 'user' ? '👤' : '🤖';
  
  const bubbleEl = node.querySelector('[data-role="bubble"]');
  bubbleEl.textContent = content;
  
  // 📚 Si hay referencias, agregarlas después del contenido
  if (references && references.length > 0) {
    const referencesContainer = document.createElement('div');
    referencesContainer.className = 'references';
    
    const referencesTitle = document.createElement('div');
    referencesTitle.className = 'references-title';
    referencesTitle.innerHTML = `📚 <strong>Referencias consultadas:</strong>`;
    referencesContainer.appendChild(referencesTitle);
    
    references.forEach(ref => {
      const refCard = document.createElement('div');
      refCard.className = 'reference-card';
      
      const refHeader = document.createElement('div');
      refHeader.className = 'reference-header';
      refHeader.innerHTML = `<span class="reference-number">${ref.id}</span> <span class="reference-title">${ref.title || ref.source}</span>`;
      
      const refUrl = document.createElement('a');
      refUrl.className = 'reference-url';
      refUrl.href = ref.source;
      refUrl.target = '_blank';
      refUrl.textContent = '🔗 Ver documento';
      
      refCard.appendChild(refHeader);
      refCard.appendChild(refUrl);
      
      referencesContainer.appendChild(refCard);
    });
    
    bubbleEl.appendChild(referencesContainer);
  }
  
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubbleEl;
}

// Envía un mensaje al backend y maneja la respuesta
async function sendMessage(message) {
  appendMessage('user', message);
  const assistantBubble = appendMessage('assistant', '...');
  statusEl.hidden = false;
  statusEl.textContent = 'Generando respuesta';

  try {
    const resp = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION_ID, message })
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    
    // 🎨 Limpiar el bubble y recrear el mensaje con referencias
    const parentArticle = assistantBubble.closest('.msg');
    parentArticle.remove();
    appendMessage('assistant', data.reply, data.references);
    
  } catch (err) {
    assistantBubble.textContent = '[Error] ' + err.message;
  } finally {
    statusEl.hidden = true;
  }
}

// Controla cuando se envía el formulario
form.addEventListener('submit', e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendMessage(text);
});

// Controla cuando se presiona una tecla en el campo de entrada
input.addEventListener('keydown', e => {

  // Si es la tecla Enter significa que se quiere enviar el mensaje
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

// Mensaje de bienvenida
appendMessage('assistant', 'Hola, ¿en qué te puedo ayudar?');