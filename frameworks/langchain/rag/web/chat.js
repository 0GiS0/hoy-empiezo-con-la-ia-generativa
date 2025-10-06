// 🌐 URL del endpoint del backend, obtenida dinámicamente por si cambia el puerto.
const API_URL = document.location.origin + '/chat';

// 🎯 Elementos del DOM
const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('input');
const statusEl = document.getElementById('status');

// 🆔 Generar / recuperar un sessionId persistente para simular usuarios distintos
function getSessionId() {
  const KEY = 'chat_session_id';
  let id = localStorage.getItem(KEY);
  if (!id) {
    // 🎲 ID sencillo: fecha base36 + 8 chars aleatorios
    const rand = Math.random().toString(36).slice(2, 10);
    id = Date.now().toString(36) + '-' + rand;
    localStorage.setItem(KEY, id);
  }
  return id;
}

// 🔑 Generar o recuperar un ID de sesión único
const SESSION_ID = getSessionId();

// 💬 Permite añadir un mensaje al chat
function appendMessage(role, content, references = null, routingAction = null) {
  const tpl = document.getElementById('message-template');
  const node = tpl.content.firstElementChild.cloneNode(true);
  node.classList.add(role === 'user' ? 'user' : 'assistant');
  
  // 🎨 Configurar avatar según el tipo de respuesta
  const avatarEl = node.querySelector('[data-role="avatar"]');
  if (role === 'user') {
    avatarEl.textContent = '👤';
  } else {
    // 🤖 Para el asistente, cambiar según si usó RAG o respuesta directa
    if (routingAction === 'retrieve') {
      avatarEl.textContent = '📚'; // Emoji de libro para RAG
      avatarEl.classList.add('rag-mode');
    } else if (routingAction === 'direct') {
      avatarEl.textContent = '⚡'; // Emoji de rayo para respuesta directa
      avatarEl.classList.add('direct-mode');
    } else {
      avatarEl.textContent = '🤖'; // Por defecto (mensaje de bienvenida, etc.)
    }
  }
  
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

// 📤 Envía un mensaje al backend y maneja la respuesta
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
    
    // 🔄 Limpiar el bubble y recrear el mensaje con referencias y tipo de routing
    const parentArticle = assistantBubble.closest('.msg');
    parentArticle.remove();
    const routingAction = data.routing?.action || null;
    appendMessage('assistant', data.reply, data.references, routingAction);
    
  } catch (err) {
    assistantBubble.textContent = '[Error] ' + err.message;
  } finally {
    statusEl.hidden = true;
  }
}

// 📝 Controla cuando se envía el formulario
form.addEventListener('submit', e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendMessage(text);
});

// ⌨️ Controla cuando se presiona una tecla en el campo de entrada
input.addEventListener('keydown', e => {

  // ⏎ Si es la tecla Enter significa que se quiere enviar el mensaje
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

// 👋 Mensaje de bienvenida
appendMessage('assistant', 'Hola, ¿en qué te puedo ayudar?');

// ⚙️ Cargar información de configuración al inicio
const INFO_URL = document.location.origin + '/info';

async function loadConfigInfo() {
  const loadingEl = document.querySelector('.config-loading');
  const modelsSection = document.getElementById('config-models');
  const providerSection = document.getElementById('config-provider');
  const vectorstoreSection = document.getElementById('config-vectorstore');
  
  try {
    const resp = await fetch(INFO_URL);
    if (!resp.ok) throw new Error('Error al cargar configuración');
    const data = await resp.json();
    
    // 🤖 Llenar información de modelos
    document.getElementById('router-model').textContent = data.config.router_model || 'No configurado';
    document.getElementById('answer-model').textContent = data.config.answer_model || 'No configurado';
    document.getElementById('embeddings-model').textContent = data.config.embeddings_model || 'No configurado';
    
    // 🔌 Llenar información del proveedor
    document.getElementById('provider-name').textContent = data.provider.name;
    document.getElementById('endpoint-url').textContent = data.provider.endpoint_url;
    document.getElementById('model-provider').textContent = data.provider.model_provider;
    
    // 🗄️ Llenar información del vector store
    document.getElementById('collection-name').textContent = data.vector_store.collection;
    document.getElementById('doc-count').textContent = data.vector_store.documents_count;
    document.getElementById('k-documents').textContent = data.config.k_documents;
    
    const statusEl = document.getElementById('doc-status');
    statusEl.className = `config-status ${data.vector_store.status}`;
    statusEl.textContent = data.vector_store.status === 'ready' ? '✓ Listo' : '⚠ Vacío';
    
    // 👁️ Mostrar secciones y ocultar loading
    loadingEl.style.display = 'none';
    modelsSection.style.display = 'block';
    providerSection.style.display = 'block';
    vectorstoreSection.style.display = 'block';
    
  } catch (err) {
    loadingEl.innerHTML = `<span style="color: var(--danger);">❌ Error: ${err.message}</span>`;
  }
}

// 🚀 Cargar configuración al inicio
loadConfigInfo();

