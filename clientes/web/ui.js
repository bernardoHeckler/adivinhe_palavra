const chatMessages = document.getElementById("chat-messages");
const statusIndicator = document.getElementById("status-indicator");
const statusText = document.getElementById("status-text");

export function updateStatus(connected, text) {
    if (connected) {
        statusIndicator.classList.add("connected");
    } else {
        statusIndicator.classList.remove("connected");
    }
    statusText.textContent = text;
}

export function addMessage(remetente, conteudo, tipo) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${tipo}`;

    const senderDiv = document.createElement("div");
    senderDiv.className = "sender";
    senderDiv.textContent = remetente;

    const contentDiv = document.createElement("div");
    contentDiv.className = "content";
    contentDiv.textContent = conteudo;

    msgDiv.appendChild(senderDiv);
    msgDiv.appendChild(contentDiv);

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
}
