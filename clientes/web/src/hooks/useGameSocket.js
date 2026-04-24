import { useState, useCallback, useRef } from 'react';

export function useGameSocket() {
    const [gameState, setGameState] = useState({
        connected: false,
        status: "Desconectado",
        room: "",
        username: "",
        players: [],
        scoreboard: [],
        roundNumber: 0,
        category: "Aguardando categoria",
        emojis: "⌛",
        subtitle: "Esperando o próximo desafio começar...",
        timer: 0,
        messages: [],
        feedback: null,
        shakeGuess: false,
        ipServidor: "",
        revealedAnswer: null,
    });

    const [ws, setWs] = useState(null);
    const timerRef = useRef(null);

    const updateState = (updates) => {
        setGameState((prev) => ({ ...prev, ...updates }));
    };

    const addMessage = useCallback((msg) => {
        const time = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
        setGameState((prev) => {
            const newMessages = [...prev.messages, { ...msg, time }];
            if (newMessages.length > 50) newMessages.shift();
            return { ...prev, messages: newMessages };
        });
    }, []);

    const showFeedback = useCallback((text, type = "warning") => {
        updateState({ feedback: { text, type }, shakeGuess: false });
        if (type === "quase") {
            setTimeout(() => updateState({ shakeGuess: true }), 50);
        }
    }, []);

    const clearFeedback = useCallback(() => {
        updateState({ feedback: null, shakeGuess: false });
    }, []);

    const startTimer = useCallback((seconds) => {
        clearInterval(timerRef.current);
        let remaining = Number(seconds) || 0;
        updateState({ timer: remaining });
        
        timerRef.current = setInterval(() => {
            remaining = Math.max(0, remaining - 1);
            setGameState(prev => ({ ...prev, timer: remaining }));
            if (remaining <= 0) {
                clearInterval(timerRef.current);
            }
        }, 1000);
    }, []);

    const handleMessage = useCallback((data, currentUsername) => {
        switch (data.tipo) {
            case "game_state":
                updateState({
                    room: data.sala || "default",
                    scoreboard: data.placar || [],
                    players: data.jogadores || [],
                    ipServidor: data.ip_servidor || "",
                });
                if (data.partida_encerrada) {
                    showFeedback("Partida encerrada. A próxima começa em instantes.", "success");
                }
                break;
            case "round_start":
                clearFeedback();
                updateState({
                    matchResult: null,
                    revealedAnswer: null,
                    roundNumber: data.rodada,
                    category: data.categoria,
                    emojis: data.emojis,
                    subtitle: "Descubra a resposta antes de todo mundo.",
                    scoreboard: data.placar || [],
                });
                startTimer(data.tempo);
                break;
            case "round_end":
                if (data.motivo === "acerto") {
                    addMessage({ author: "Sistema", text: `✅ ${data.vencedor} acertou!`, type: "success" });
                } else {
                    showFeedback(`⏱️ Tempo esgotado!`, "warning");
                }
                updateState({ 
                    scoreboard: data.placar || [],
                    revealedAnswer: data.resposta
                });
                clearInterval(timerRef.current);
                break;
            case "match_end":
                const top3 = (data.placar || []).slice(0, 3);
                updateState({
                    matchResult: { 
                        winner: data.vencedor, 
                        score: data.pontuacao, 
                        target: data.alvo, 
                        top3,
                        prontos: data.prontos || 0,
                        total_jogadores: data.total_jogadores || 0
                    },
                    subtitle: "Aguardando jogadores para nova disputa.",
                    scoreboard: data.placar || []
                });
                clearInterval(timerRef.current);
                break;
            case "match_ready_update":
                setGameState(prev => {
                    if (prev.matchResult) {
                        return { ...prev, matchResult: { ...prev.matchResult, prontos: data.prontos, total_jogadores: data.total_jogadores } };
                    }
                    return prev;
                });
                break;
            case "scoreboard":
                updateState({ scoreboard: data.placar || [] });
                break;
            case "player_list":
                updateState({ players: data.jogadores || [] });
                break;
            case "system":
                if (data.tipo_sys === "quase") {
                    showFeedback(`🔥 ${data.texto}`, "quase");
                } else if (data.tipo_sys === "dica") {
                    showFeedback(`💡 ${data.texto}`, "warning");
                } else if (data.tipo_sys === "sucesso") {
                    addMessage({ author: "Sistema", text: data.texto, type: "success" });
                    break;
                } else {
                    addMessage({ author: "Sistema", text: data.texto, type: "system" });
                }
                break;
            case "chat":
                addMessage({
                    author: data.usuario || "Jogador",
                    text: data.quase ? `${data.texto} (quase)` : data.texto,
                    type: data.usuario === currentUsername ? "self" : "other",
                });
                break;
            default:
                break;
        }
    }, [addMessage, clearFeedback, showFeedback, startTimer]);

    const connect = useCallback((room, username) => {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === "https:" ? "wss" : "ws";
            const host = window.location.port === "5173" ? "localhost:8081" : window.location.host;
            
            const params = new URLSearchParams({ sala: room, usuario: username });
            const socket = new WebSocket(`${protocol}://${host}/chat/ws?${params.toString()}`);

            socket.onopen = () => {
                updateState({ connected: true, status: "Online", room, username });
                addMessage({ author: "Sistema", text: `Você entrou na sala ${room}.`, type: "system" });
                setWs(socket);
                resolve(socket);
            };

            socket.onmessage = (event) => {
                try {
                    handleMessage(JSON.parse(event.data), username);
                } catch (error) {
                    console.error("Falha ao processar mensagem do servidor", error);
                }
            };

            socket.onclose = () => {
                updateState({ connected: false, status: "Desconectado" });
                clearInterval(timerRef.current);
                addMessage({ author: "Sistema", text: "Conexão encerrada. Recarregue para voltar.", type: "system" });
                setWs(null);
            };

            socket.onerror = (error) => {
                updateState({ connected: false, status: "Erro" });
                reject(error);
            };
        });
    }, [addMessage, handleMessage]);

    const sendGuess = useCallback((text) => {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            return false;
        }
        ws.send(JSON.stringify({ tipo: "guess", texto: text }));
        return true;
    }, [ws]);

    const sendReady = useCallback(() => {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            return false;
        }
        ws.send(JSON.stringify({ tipo: "pronto" }));
        return true;
    }, [ws]);

    return { gameState, connect, sendGuess, sendReady };
}
