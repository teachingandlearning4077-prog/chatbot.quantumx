const form = document.getElementById('chat-form');
const input = document.getElementById('message');
const chatWindow = document.getElementById('chat-window');
const modeSelect = document.getElementById('mode');
const statusLabel = document.getElementById('status');
const quickActions = document.getElementById('quick-actions');

function setStatus(text) {
  if (statusLabel) statusLabel.textContent = text;
}

function appendMessage(text, cls) {
  const bubble = document.createElement('div');
  bubble.className = `msg ${cls}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return bubble;
}

function appendGeneratedImage(base64) {
  if (!base64) return;
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';

  const title = document.createElement('div');
  title.textContent = 'Imagem gerada:';
  wrap.appendChild(title);

  const image = document.createElement('img');
  image.className = 'generated-image';
  image.alt = 'Imagem gerada pelo QuantumX';
  image.src = `data:image/png;base64,${base64}`;
  wrap.appendChild(image);

  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function applyQuickAction(prompt) {
  input.value = prompt;
  if (prompt.toLowerCase().includes('desenhe') || prompt.toLowerCase().includes('imagem')) {
    modeSelect.value = 'image';
  } else {
    modeSelect.value = 'text';
  }
  input.focus();
}

appendMessage('Olá! Eu sou o QuantumX. Escolha o modo de texto ou imagem e me peça qualquer coisa.', 'bot');

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

  const formData = new FormData();
  formData.append('message', message);
  formData.append('mode', mode);

  try {
    const response = await fetch('/chat', { method: 'POST', body: formData });
    if (!response.ok) {
      appendMessage(`Erro do servidor (${response.status}).`, 'bot');
      setStatus('Erro');
      return;
    }

    const data = await response.json();
    appendMessage(data.response || 'Sem resposta no momento.', 'bot');
    appendGeneratedImage(data.image_base64);
    setStatus('Pronto');
  } catch (error) {
    appendMessage('Erro de conexão. Tente novamente.', 'bot');
    setStatus('Sem conexão');
  }
});
