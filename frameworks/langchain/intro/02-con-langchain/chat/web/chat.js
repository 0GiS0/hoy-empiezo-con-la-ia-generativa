// Endpoint actualizado (modo invoke no streaming)
const API_URL = 'http://127.0.0.1:5500/chat';

const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('input');
const sourceSelect = document.getElementById('source');
const emojiToggle = document.getElementById('emoji-toggle');
const emojiPanel = document.getElementById('emoji-panel');
const statusEl = document.getElementById('status');

// Historial en memoria (formato similar al backend existente)
const history = [];

// Set básico de emojis (se puede ampliar)
const EMOJIS = '😀 😃 😄 😁 😆 😅 🤣 😂 🙂 🙃 😉 😊 😇 🥰 😍 🤩 😘 😗 😋 😜 🤪 🤨 🧐 🤓 😎 🥳 😏 😒 😞 😔 😟 😕 🙁 😣 😖 😫 😩 🥺 😢 😭 😤 😠 😡 🤯 😳 🥵 🥶 😱 😨 😰 😥 😓 🤗 🤔 🤭 🤫 🤥 😶 😐 😑 😬 🙄 😯 😦 😧 😮 😲 🥱 😴 🤤 😪 😵 🤐 🥴 🤢 🤮 🤧 😷 🤒 🤕 😈 👿 👻 💀 ☠️ 🤖 🎃 🤡 👽 👾 🤝 🙌 👏 👍 👎 👊 🤛 🤜 🤞 ✌️ 🤘 🤟 👌 🤌 🤏 ✋ 🤚 🖐️ 🖖 👋 🤙 💪'.split(/\s+/);

function buildEmojiPanel(){
  EMOJIS.forEach(e => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = e;
    btn.addEventListener('click', () => {
      input.value += e;
      input.focus();
    });
    emojiPanel.appendChild(btn);
  });
}

function toggleEmojiPanel(){
  const expanded = emojiToggle.getAttribute('aria-expanded') === 'true';
  emojiToggle.setAttribute('aria-expanded', String(!expanded));
  emojiPanel.hidden = expanded;
}

emojiToggle.addEventListener('click', toggleEmojiPanel);

document.addEventListener('click', (e)=>{
  if(!emojiPanel.hidden && !emojiPanel.contains(e.target) && e.target !== emojiToggle){
    toggleEmojiPanel();
  }
});

function autoGrow(){
  input.style.height = 'auto';
  input.style.height = (input.scrollHeight) + 'px';
}
input.addEventListener('input', autoGrow);

function appendMessage(role, content, streaming=false){
  const tpl = document.getElementById('message-template');
  const node = tpl.content.firstElementChild.cloneNode(true);
  node.classList.add(role === 'user' ? 'user' : 'assistant');
  if(streaming) node.classList.add('streaming');
  node.querySelector('[data-role="avatar"]').textContent = role === 'user' ? '👤' : '🤖';
  node.querySelector('[data-role="bubble"]').textContent = content;
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return node.querySelector('[data-role="bubble"]');
}

async function sendMessage(message){
  history.push({ role: 'user', content: message });
  appendMessage('user', message);
  const assistantBubble = appendMessage('assistant', '…');
  statusEl.hidden = false;
  statusEl.textContent = 'Generando respuesta…';

  const threadId = 'demo-thread'; // se puede hacer dinámico
  const payload = { thread_id: threadId, message };

  try {
    const resp = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if(!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    assistantBubble.textContent = data.reply;
    history.push({ role: 'assistant', content: data.reply });
  } catch(err){
    assistantBubble.textContent = '[Error] ' + err.message;
  } finally {
    statusEl.hidden = true;
  }
}

form.addEventListener('submit', (e)=>{
  e.preventDefault();
  const text = input.value.trim();
  if(!text) return;
  input.value = '';
  autoGrow();
  sendMessage(text);
});

// UX: Enviar con Ctrl+Enter manteniendo saltos con Shift+Enter
input.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    form.requestSubmit();
  }
});

buildEmojiPanel();
autoGrow();
appendMessage('assistant', '¡Hola! Soy tu asistente 🤖. ¿En qué te ayudo hoy?');
