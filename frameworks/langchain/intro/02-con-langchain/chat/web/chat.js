// URL del endpoint del backend
const API_URL = 'http://127.0.0.1:5500/chat';

// Referencias básicas
const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('input');
const statusEl = document.getElementById('status');

// Generar / recuperar un threadId persistente para simular usuarios distintos
function getThreadId(){
  const KEY = 'chat_thread_id';
  let id = localStorage.getItem(KEY);
  if(!id){
    // ID sencillo: fecha base36 + 8 chars aleatorios
    const rand = Math.random().toString(36).slice(2, 10);
    id = Date.now().toString(36) + '-' + rand;
    localStorage.setItem(KEY, id);
  }
  return id;
}
const THREAD_ID = getThreadId();

function appendMessage(role, content){
  const tpl = document.getElementById('message-template');
  const node = tpl.content.firstElementChild.cloneNode(true);
  node.classList.add(role === 'user' ? 'user' : 'assistant');
  node.querySelector('[data-role="avatar"]').textContent = role === 'user' ? '👤' : '🤖';
  node.querySelector('[data-role="bubble"]').textContent = content;
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return node.querySelector('[data-role="bubble"]');
}

async function sendMessage(message){
  appendMessage('user', message);
  const assistantBubble = appendMessage('assistant', '...');
  statusEl.hidden = false;
  statusEl.textContent = 'Generando respuesta';

  try {
    const resp = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ thread_id: THREAD_ID, message })
    });
    if(!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    assistantBubble.textContent = data.reply;
  } catch (err) {
    assistantBubble.textContent = '[Error] ' + err.message;
  } finally {
    statusEl.hidden = true;
  }
}

form.addEventListener('submit', e => {
  e.preventDefault();
  const text = input.value.trim();
  if(!text) return;
  input.value = '';
  sendMessage(text);
});

input.addEventListener('keydown', e => {
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    form.requestSubmit();
  }
});

appendMessage('assistant', 'Hola, ¿en qué te puedo ayudar?');
