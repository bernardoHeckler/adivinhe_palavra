import { preencherSalaInicial, abrirJogo, obterElementos, limparCampo } from "./ui.js";
import { conectar, enviarPalpite } from "./websocket.js";

document.addEventListener("DOMContentLoaded", () => {
    preencherSalaInicial();
    const elements = obterElementos();

    let sessaoAtual = null;

    elements.loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const usuario = elements.usernameInput.value.trim();
        const sala = elements.roomInput.value.trim() || "default";

        if (!usuario) {
            elements.usernameInput.focus();
            return;
        }

        try {
            sessaoAtual = { usuario, sala };
            await conectar(sessaoAtual);
            abrirJogo(sessaoAtual);
            const params = new URLSearchParams(window.location.search);
            params.set("sala", sala);
            window.history.replaceState({}, "", `?${params.toString()}`);
        } catch (error) {
            console.error("Não foi possível conectar", error);
            sessaoAtual = null;
        }
    });

    elements.guessForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const texto = elements.guessInput.value.trim();
        if (!texto || !sessaoAtual) {
            return;
        }
        if (enviarPalpite(texto)) {
            limparCampo();
        }
    });
});
