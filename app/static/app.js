const form = document.getElementById('chat-form');
const input = document.getElementById('message');
const chatWindow = document.getElementById('chat-window');
const modeSelect = document.getElementById('mode');
const statusLabel = document.getElementById('status');
const quickActions = document.getElementById('quick-actions');
const themeButtons = document.querySelectorAll('.theme-btn');

function setStatus(text) {
  if (statusLabel) statusLabel.textContent = text;
}

function appendMessage(text, cls) {
  const bubble = document.createElement('div');
  bubble.className = `msg ${cls}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function appendGeneratedImage(base64) {
  if (!base64) return;
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';
  wrap.innerHTML = '<div>Imagem gerada:</div>';

  const image = document.createElement('img');
  image.className = 'generated-image';
  image.alt = 'Imagem gerada pelo QuantumX';
  image.src = `data:image/png;base64,${base64}`;
  wrap.appendChild(image);

  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function localReply(message, mode) {
  const text = message.toLowerCase();
  if (mode === 'image') {
    return 'Sem API externa, não consigo renderizar imagem real agora. Mas posso criar um prompt perfeito para você usar em qualquer gerador de imagem.';
  }
  if (text.includes('calcule') || text.includes('quanto é')) {
    return 'Posso calcular! Exemplo: "calcule 25*14".';
  }
  if (text.includes('resuma')) {
    return 'Envie o texto completo e eu te devolvo um resumo em tópicos.';
  }
  if (text.includes('lista')) {
    return 'Claro! Posso montar uma checklist com prioridades e prazos.';
  }
  return 'Estou online ✅. Posso responder perguntas, criar ideias, ajudar com estudos, programação e planejamento.';
}

async function askServer(message, mode) {
  const formData = new FormData();
  formData.append('message', message);
  formData.append('mode', mode);

  const response = await fetch('/chat', { method: 'POST', body: formData });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

function applyQuickAction(prompt) {
  input.value = prompt;
  modeSelect.value = prompt.toLowerCase().includes('desenhe') ? 'image' : 'text';
  input.focus();
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('qx-theme', theme);
}

appendMessage('Olá! Eu sou o QuantumX. Agora o chat funciona com servidor ou em fallback local no navegador.', 'bot');

const savedTheme = localStorage.getItem('qx-theme');
if (savedTheme) applyTheme(savedTheme);

themeButtons.forEach((btn) => {
  btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
});

if (quickActions) {
  quickActions.addEventListener('click', (event) => {
    const button = event.target.closest('button[data-prompt]');
    if (!button) return;
    applyQuickAction(button.dataset.prompt || '');
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  const mode = modeSelect.value;
  if (!message) return;

  appendMessage(`${mode === 'image' ? '[Imagem] ' : ''}${message}`, 'user');
  input.value = '';
  setStatus('Processando...');

  try {
    const data = await askServer(message, mode);
    appendMessage(data.response || 'Sem resposta no momento.', 'bot');
    appendGeneratedImage(data.image_base64);
    setStatus('Pronto');
  } catch (error) {
    appendMessage(localReply(message, mode), 'bot');
    setStatus('Fallback local ativo');
  }
});
