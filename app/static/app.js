const form = document.getElementById('chat-form');
const input = document.getElementById('message');
const chatWindow = document.getElementById('chat-window');

function appendMessage(text, cls) {
  const bubble = document.createElement('div');
  bubble.className = `msg ${cls}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

appendMessage('Olá! Eu sou o QuantumX. Como posso ajudar hoje?', 'bot');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, 'user');
  input.value = '';

  const formData = new FormData();
  formData.append('message', message);

  const response = await fetch('/chat', {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  appendMessage(data.response || 'Sem resposta no momento.', 'bot');
});
