import {
    adicionarMensagem,
    atualizarEstadoInicial,
    atualizarStatus,
    atualizarTimer,
    destacarQuase,
    encerrarRodada,
    encerrarPartida,
    iniciarRodada,
    limparFeedback,
    renderizarJogadores,
    renderizarPlacar,
    mostrarFeedback,
} from "./ui.js";

let ws;
let temporizador;

function montarUrl(sala, usuario) {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const params = new URLSearchParams({ sala, usuario });
    return `${protocol}://${window.location.host}/chat/ws?${params.toString()}`;
}

function iniciarContagem(segundos) {
    clearInterval(temporizador);
    let restante = Number(segundos) || 0;
    atualizarTimer(restante);
    temporizador = window.setInterval(() => {
        restante = Math.max(0, restante - 1);
        atualizarTimer(restante);
        if (restante <= 0) {
            clearInterval(temporizador);
        }
    }, 1000);
}

function tratarMensagem(data, usuarioAtual) {
    switch (data.tipo) {
        case "game_state":
            atualizarEstadoInicial(data);
            break;
        case "round_start":
            limparFeedback();
            iniciarRodada(data);
            renderizarPlacar(data.placar || []);
            iniciarContagem(data.tempo);
            break;
        case "round_end":
            encerrarRodada(data);
            renderizarPlacar(data.placar || []);
            clearInterval(temporizador);
            break;
        case "match_end":
            encerrarPartida(data);
            renderizarPlacar(data.placar || []);
            clearInterval(temporizador);
            break;
        case "scoreboard":
            renderizarPlacar(data.placar || []);
            break;
        case "player_list":
            renderizarJogadores(data.jogadores || []);
            break;
        case "system":
            if (data.tipo_sys === "quase") {
                mostrarFeedback(`🔥 ${data.texto}`, "warning");
                destacarQuase();
            } else if (data.tipo_sys === "dica") {
                mostrarFeedback(`💡 ${data.texto}`, "warning");
            }
            adicionarMensagem({ autor: "Sistema", texto: data.texto, tipo: "system" });
            break;
        case "chat":
            adicionarMensagem({
                autor: data.usuario || "Jogador",
                texto: data.quase ? `${data.texto} (quase)` : data.texto,
                tipo: data.usuario === usuarioAtual ? "self" : "other",
            });
            break;
        default:
            break;
    }
}

export function conectar({ sala, usuario }) {
    return new Promise((resolve, reject) => {
        ws = new WebSocket(montarUrl(sala, usuario));

        ws.onopen = () => {
            atualizarStatus(true, "Online");
            adicionarMensagem({ autor: "Sistema", texto: `Você entrou na sala ${sala}.`, tipo: "system" });
            resolve();
        };

        ws.onmessage = (event) => {
            try {
                tratarMensagem(JSON.parse(event.data), usuario);
            } catch (error) {
                console.error("Falha ao processar mensagem do servidor", error);
            }
        };

        ws.onclose = () => {
            atualizarStatus(false, "Desconectado");
            clearInterval(temporizador);
            adicionarMensagem({ autor: "Sistema", texto: "Conexão encerrada. Recarregue para voltar.", tipo: "system" });
        };

        ws.onerror = (error) => {
            atualizarStatus(false, "Erro");
            reject(error);
        };
    });
}

export function enviarPalpite(texto) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        return false;
    }
    ws.send(JSON.stringify({ tipo: "guess", texto }));
    return true;
}
