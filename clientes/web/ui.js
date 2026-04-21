const elements = {
    loginForm: document.getElementById("login-form"),
    usernameInput: document.getElementById("username-input"),
    roomInput: document.getElementById("room-input"),
    gameLayout: document.getElementById("game-layout"),
    roomLabel: document.getElementById("room-label"),
    roundLabel: document.getElementById("round-label"),
    timerValue: document.getElementById("timer-value"),
    timerBadge: document.getElementById("timer-badge"),
    categoryLabel: document.getElementById("category-label"),
    emojiDisplay: document.getElementById("emoji-display"),
    stageSubtitle: document.getElementById("stage-subtitle"),
    feedbackBanner: document.getElementById("feedback-banner"),
    guessForm: document.getElementById("guess-form"),
    guessInput: document.getElementById("guess-input"),
    scoreboard: document.getElementById("scoreboard"),
    messages: document.getElementById("messages"),
    playerCount: document.getElementById("player-count"),
    connectionStatus: document.getElementById("connection-status"),
};

function escapeHtml(texto) {
    return texto
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}

export function preencherSalaInicial() {
    const params = new URLSearchParams(window.location.search);
    elements.roomInput.value = params.get("sala") || "default";
}

export function abrirJogo({ usuario, sala }) {
    elements.loginForm.classList.add("hidden");
    elements.gameLayout.classList.remove("hidden");
    elements.roomLabel.textContent = sala;
    elements.stageSubtitle.textContent = `Boa sorte, ${usuario}. O chat também vale como tentativa.`;
    elements.guessInput.focus();
}

export function atualizarStatus(conectado, texto) {
    elements.connectionStatus.textContent = texto;
    elements.connectionStatus.classList.toggle("online", conectado);
    elements.connectionStatus.classList.toggle("offline", !conectado);
}

export function atualizarEstadoInicial(estado) {
    elements.roomLabel.textContent = estado.sala || "default";
    renderizarPlacar(estado.placar || []);
    renderizarJogadores(estado.jogadores || []);
    if (estado.partida_encerrada) {
        mostrarFeedback("Partida encerrada. A próxima começa em instantes.", "success");
    }
}

export function iniciarRodada({ rodada, emojis, categoria, tempo }) {
    elements.roundLabel.textContent = `Rodada ${rodada}`;
    elements.categoryLabel.textContent = categoria;
    elements.emojiDisplay.textContent = emojis;
    elements.stageSubtitle.textContent = "Descubra a resposta antes de todo mundo.";
    atualizarTimer(tempo);
}

export function encerrarRodada({ motivo, vencedor, resposta }) {
    if (motivo === "acerto") {
        mostrarFeedback(`✅ ${vencedor} acertou: ${resposta}`, "success");
    } else {
        mostrarFeedback(`⏱️ Tempo esgotado. A resposta era: ${resposta}`, "warning");
    }
}

export function encerrarPartida({ vencedor, pontuacao, alvo }) {
    mostrarFeedback(`🏆 ${vencedor} venceu a partida com ${pontuacao} pontos de ${alvo}.`, "success");
    elements.stageSubtitle.textContent = "Placares zeram em instantes para uma nova disputa.";
}

export function atualizarTimer(segundos) {
    elements.timerValue.textContent = String(segundos).padStart(2, "0");
    elements.timerBadge.style.borderColor =
        segundos <= 10 ? "rgba(239, 68, 68, 0.45)" :
        segundos <= 20 ? "rgba(249, 115, 22, 0.45)" :
        "rgba(148, 163, 184, 0.18)";
}

export function renderizarPlacar(placar) {
    if (!placar.length) {
        elements.scoreboard.innerHTML = '<p class="stage-subtitle">Ainda sem pontos.</p>';
        return;
    }

    const medalhas = ["🥇", "🥈", "🥉"];
    elements.scoreboard.innerHTML = placar
        .map((item, index) => `
            <div class="score-row">
                <strong>${medalhas[index] || "🎯"} ${escapeHtml(item.usuario)}</strong>
                <span>${item.pontos} pts</span>
            </div>
        `)
        .join("");
}

export function renderizarJogadores(jogadores) {
    const total = jogadores.length;
    elements.playerCount.textContent = `${total} jogador${total === 1 ? "" : "es"}`;
}

export function adicionarMensagem({ autor, texto, tipo = "system" }) {
    const classe = tipo === "self" ? "message self" : tipo === "system" ? "message system" : "message";
    const horario = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    const conteudo = texto ? escapeHtml(texto) : "";

    const item = document.createElement("article");
    item.className = classe;
    item.innerHTML = `
        <div class="meta">
            <strong>${escapeHtml(autor)}</strong>
            <span>${horario}</span>
        </div>
        <p>${conteudo}</p>
    `;
    elements.messages.appendChild(item);
    elements.messages.scrollTop = elements.messages.scrollHeight;
}

export function mostrarFeedback(texto, variante = "warning") {
    elements.feedbackBanner.textContent = texto;
    elements.feedbackBanner.className = `feedback-banner ${variante}`;
}

export function limparFeedback() {
    elements.feedbackBanner.className = "feedback-banner hidden";
    elements.feedbackBanner.textContent = "";
}

export function destacarQuase() {
    elements.guessInput.classList.remove("shake");
    void elements.guessInput.offsetWidth;
    elements.guessInput.classList.add("shake");
}

export function limparCampo() {
    elements.guessInput.value = "";
}

export function obterElementos() {
    return elements;
}
