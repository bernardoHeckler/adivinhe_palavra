import { addMessage, updateStatus } from './ui.js';

let ws;
function getWsUrl(){
    const parametros = new URLSearchParams(window.location.search);
    const sala = parametros.get("sala") || "default";
    return `ws://${window.location.host}/chat/ws?sala=${sala}`;
}

const wsUrl = getWsUrl();

export function connect() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        updateStatus(true, "Conexão Instanciada");
        addMessage(
            "Sistema",
            `Conectado na sala: ${new URLSearchParams(window.location.search).get("sala") || "default"}`,
            "servidor"
        );
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            addMessage(
                data.remetente || "Desconhecido",
                data.conteudo,
                "servidor"
            );
        } catch (e) {
            console.error("Erro ao fazer o parse da mensagem JSON", e);
        }
    };

    ws.onclose = () => {
        updateStatus(false, "Offline (Tentando reconectar...)");
        addMessage("Sistema", "Conexão perdida. Reconectando em 3 Segundos...", "servidor");
        setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
        console.error("Erro capturado no Canal WebSocket:", error);
    };
}

export function sendMessage(remetente, texto) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const payload = {
            remetente: remetente,
            conteudo: texto,
        };
        ws.send(JSON.stringify(payload));
        return payload;
    }
    console.warn("WebSocket não está conectado.");
    return null;
}
