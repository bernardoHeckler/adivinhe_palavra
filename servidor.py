import asyncio
import json
import random
import time
import socket
from logging import Logger

import tornado.websocket

from logger import obter_logger
from protocolo import (
    DESAFIOS,
    MSG_CHAT,
    MSG_GAME_STATE,
    MSG_GUESS,
    MSG_MATCH_END,
    MSG_PLAYER_LIST,
    MSG_ROUND_END,
    MSG_ROUND_START,
    MSG_SCOREBOARD,
    MSG_SYSTEM,
    ChatMessage,
    desserializar,
    serializar,
    verificar_palpite,
)

log_servidor: Logger = obter_logger("Servidor")

def obter_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

TEMPO_RODADA = 60
TEMPO_PROXIMA_RODADA = 4
PONTOS_POR_COLOCACAO = (30, 20, 15, 10)
PONTOS_MINIMOS_ACERTO = 5
PONTOS_VITORIA_PARTIDA = 300
MARCOS_DICA = (20, 40)


class SalaJogo:
    def __init__(self, nome: str):
        self.nome = nome
        self.conexoes: set[ChatHandler] = set()
        self.pontuacoes: dict[str, int] = {}
        self.rodada_atual: dict | None = None
        self.rodada_numero = 0
        self.desafios_usados: list[dict] = []
        self.timer_task: asyncio.Task | None = None
        self.reinicio_task: asyncio.Task | None = None
        self.vencedor_rodada: str | None = None
        self.partida_encerrada = False
        self.jogadores_prontos: set[str] = set()

    def adicionar_jogador(self, conexao: "ChatHandler") -> None:
        self.conexoes.add(conexao)
        self.pontuacoes.setdefault(conexao.usuario, 0)

    def remover_jogador(self, conexao: "ChatHandler") -> None:
        self.conexoes.discard(conexao)
        if not self.conexoes:
            self.cancelar_agendamentos()
            self.rodada_atual = None
            self.vencedor_rodada = None
            self.partida_encerrada = False
            self.jogadores_prontos.clear()

    def cancelar_agendamentos(self) -> None:
        for task in (self.timer_task, self.reinicio_task):
            if task and not task.done():
                task.cancel()

    def estado_placar(self) -> list[dict]:
        return sorted(
            [{"usuario": usuario, "pontos": pontos} for usuario, pontos in self.pontuacoes.items()],
            key=lambda item: (-item["pontos"], item["usuario"].lower()),
        )

    def estado_jogadores(self) -> list[str]:
        return sorted({conexao.usuario for conexao in self.conexoes}, key=str.lower)

    def total_jogadores(self) -> int:
        return len({conexao.usuario for conexao in self.conexoes})

    def pontos_por_colocacao(self, colocacao: int) -> int:
        if colocacao <= len(PONTOS_POR_COLOCACAO):
            return PONTOS_POR_COLOCACAO[colocacao - 1]
        return PONTOS_MINIMOS_ACERTO

    def obter_vencedor_partida(self) -> str | None:
        vencedor_partida = None
        for user, pts in self.pontuacoes.items():
            if pts >= PONTOS_VITORIA_PARTIDA:
                if not vencedor_partida or pts > self.pontuacoes[vencedor_partida]:
                    vencedor_partida = user
        return vencedor_partida

    def proximo_desafio(self) -> dict:
        disponiveis = [desafio for desafio in DESAFIOS if desafio not in self.desafios_usados]
        if not disponiveis:
            self.desafios_usados.clear()
            disponiveis = DESAFIOS[:]
        desafio = random.choice(disponiveis)
        self.desafios_usados.append(desafio)
        return desafio

    async def enviar(self, conexao: "ChatHandler", mensagem: str) -> None:
        try:
            await conexao.write_message(mensagem)
        except tornado.websocket.WebSocketClosedError:
            self.conexoes.discard(conexao)

    async def broadcast(self, mensagem: str, excluir: "ChatHandler | None" = None) -> None:
        mortos = []
        for conexao in list(self.conexoes):
            if conexao is excluir:
                continue
            try:
                await conexao.write_message(mensagem)
            except tornado.websocket.WebSocketClosedError:
                mortos.append(conexao)
        for conexao in mortos:
            self.conexoes.discard(conexao)

    async def broadcast_placar(self) -> None:
        await self.broadcast(serializar(MSG_SCOREBOARD, placar=self.estado_placar()))

    async def broadcast_jogadores(self) -> None:
        await self.broadcast(serializar(MSG_PLAYER_LIST, jogadores=self.estado_jogadores()))

    async def iniciar_rodada(self) -> None:
        if not self.conexoes or self.partida_encerrada:
            return

        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()

        desafio = self.proximo_desafio()
        self.rodada_numero += 1
        self.vencedor_rodada = None
        self.rodada_atual = {
            "desafio": desafio,
            "inicio": time.time(),
            "dicas_enviadas": 0,
            "acertadores": set(),
            "ordem_acertos": [],
        }

        await self.broadcast(
            serializar(
                MSG_ROUND_START,
                rodada=self.rodada_numero,
                emojis=desafio["emojis"],
                categoria=desafio["categoria"],
                tempo=TEMPO_RODADA,
                placar=self.estado_placar(),
            )
        )
        self.timer_task = asyncio.create_task(self._rodada_loop())

    async def _rodada_loop(self) -> None:
        try:
            while self.rodada_atual:
                await asyncio.sleep(1)
                decorrido = int(time.time() - self.rodada_atual["inicio"])
                restante = max(0, TEMPO_RODADA - decorrido)

                dicas = self.rodada_atual["desafio"]["dicas"]
                dicas_enviadas = self.rodada_atual["dicas_enviadas"]
                if dicas_enviadas < len(MARCOS_DICA) and decorrido >= MARCOS_DICA[dicas_enviadas]:
                    self.rodada_atual["dicas_enviadas"] += 1
                    if dicas_enviadas < len(dicas):
                        await self.broadcast(
                            serializar(
                                MSG_SYSTEM,
                                texto=f"Dica: {dicas[dicas_enviadas]}",
                                tipo_sys="dica",
                            )
                        )

                if restante <= 0:
                    resposta = self.rodada_atual["desafio"]["resposta"]
                    self.rodada_atual = None
                    await self.broadcast(
                        serializar(
                            MSG_ROUND_END,
                            motivo="tempo",
                            resposta=resposta,
                            placar=self.estado_placar(),
                        )
                    )

                    vencedor_partida = self.obter_vencedor_partida()
                    if vencedor_partida:
                        await self.encerrar_partida(vencedor_partida)
                        return

                    self.agendar_proxima_rodada()
                    return
        except asyncio.CancelledError:
            return

    def agendar_proxima_rodada(self) -> None:
        if self.partida_encerrada:
            return
        if self.reinicio_task and not self.reinicio_task.done():
            self.reinicio_task.cancel()
        self.reinicio_task = asyncio.create_task(self._reiniciar_apos_intervalo())

    async def _reiniciar_apos_intervalo(self) -> None:
        try:
            await asyncio.sleep(TEMPO_PROXIMA_RODADA)
            if self.conexoes:
                await self.iniciar_rodada()
        except asyncio.CancelledError:
            return

    async def processar_palpite(self, conexao: "ChatHandler", texto: str) -> None:
        if self.partida_encerrada:
            await self.broadcast(serializar(MSG_CHAT, usuario=conexao.usuario, texto=texto))
            return

        if not self.rodada_atual:
            await self.broadcast(serializar(MSG_CHAT, usuario=conexao.usuario, texto=texto))
            return

        acertou, quase = verificar_palpite(texto, self.rodada_atual["desafio"]["resposta"])
        if acertou:
            if conexao.usuario in self.rodada_atual.get("acertadores", set()):
                return

            self.rodada_atual.setdefault("acertadores", set()).add(conexao.usuario)
            ordem_acertos = self.rodada_atual.setdefault("ordem_acertos", [])
            ordem_acertos.append(conexao.usuario)
            colocacao = len(ordem_acertos)
            pontos_ganhos = self.pontos_por_colocacao(colocacao)
            self.pontuacoes[conexao.usuario] = self.pontuacoes.get(conexao.usuario, 0) + pontos_ganhos

            await self.broadcast(
                serializar(
                    MSG_SYSTEM,
                    texto=f"✅ {conexao.usuario} acertou em {colocacao}º lugar e ganhou {pontos_ganhos} pontos!",
                    tipo_sys="sucesso"
                )
            )
            await self.broadcast_placar()

            if self.total_jogadores() == 1:
                resposta = self.rodada_atual["desafio"]["resposta"]
                self.rodada_atual = None
                await self.broadcast(
                    serializar(
                        MSG_ROUND_END,
                        motivo="acerto",
                        vencedor=conexao.usuario,
                        resposta=resposta,
                        placar=self.estado_placar(),
                    )
                )

                if self.pontuacoes[conexao.usuario] >= PONTOS_VITORIA_PARTIDA:
                    await self.encerrar_partida(conexao.usuario)
                    return

                self.agendar_proxima_rodada()
                return

            return

        if quase:
            await self.enviar(
                conexao,
                serializar(
                    MSG_SYSTEM,
                    texto="Quase! Seu palpite está muito perto.",
                    tipo_sys="quase",
                ),
            )
            await self.broadcast(
                serializar(MSG_CHAT, usuario=conexao.usuario, texto=texto, quase=True)
            )
            return

        await self.broadcast(serializar(MSG_CHAT, usuario=conexao.usuario, texto=texto))

    async def encerrar_partida(self, vencedor: str) -> None:
        self.partida_encerrada = True
        self.rodada_atual = None
        self.jogadores_prontos.clear()
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        if self.reinicio_task and not self.reinicio_task.done():
            self.reinicio_task.cancel()

        await self.broadcast(
            serializar(
                MSG_MATCH_END,
                vencedor=vencedor,
                pontuacao=self.pontuacoes.get(vencedor, 0),
                alvo=PONTOS_VITORIA_PARTIDA,
                placar=self.estado_placar(),
                prontos=0,
                total_jogadores=len(self.conexoes)
            )
        )

    async def _reiniciar_partida(self) -> None:
        self.pontuacoes = {conexao.usuario: 0 for conexao in self.conexoes}
        self.rodada_atual = None
        self.rodada_numero = 0
        self.vencedor_rodada = None
        self.partida_encerrada = False
        self.jogadores_prontos.clear()
        await self.broadcast_placar()
        if self.conexoes:
            await self.broadcast(
                serializar(
                    MSG_SYSTEM,
                    texto="Nova partida iniciando.",
                    tipo_sys="reinicio_partida",
                )
            )
            await self.iniciar_rodada()

    async def registrar_pronto(self, conexao: "ChatHandler") -> None:
        if not self.partida_encerrada:
            return
        
        self.jogadores_prontos.add(conexao.usuario)
        total = len(self.conexoes)
        prontos = len(self.jogadores_prontos)
        
        await self.broadcast(
            serializar(
                "match_ready_update",
                prontos=prontos,
                total_jogadores=total
            )
        )
        
        if prontos >= total / 2: # Maioria
            await self._reiniciar_partida()

    async def enviar_estado_inicial(self, conexao: "ChatHandler") -> None:
        await self.enviar(
            conexao,
            serializar(
                MSG_GAME_STATE,
                sala=self.nome,
                usuario=conexao.usuario,
                jogadores=self.estado_jogadores(),
                placar=self.estado_placar(),
                rodada=self.rodada_numero,
                alvo_vitoria=PONTOS_VITORIA_PARTIDA,
                partida_encerrada=self.partida_encerrada,
                ip_servidor=obter_ip_local(),
            ),
        )
        if self.rodada_atual:
            restante = max(0, TEMPO_RODADA - int(time.time() - self.rodada_atual["inicio"]))
            await self.enviar(
                conexao,
                serializar(
                    MSG_ROUND_START,
                    rodada=self.rodada_numero,
                    emojis=self.rodada_atual["desafio"]["emojis"],
                    categoria=self.rodada_atual["desafio"]["categoria"],
                    tempo=restante,
                    placar=self.estado_placar(),
                    reentrada=True,
                ),
            )


salas: dict[str, SalaJogo] = {}


def obter_sala(nome: str) -> SalaJogo:
    if nome not in salas:
        salas[nome] = SalaJogo(nome)
    return salas[nome]


class ChatHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self) -> None:
        self.sala_id = self.get_argument("sala", "default")
        usuario = self.get_argument("usuario", "").strip()
        self.usuario = usuario or f"Jogador{random.randint(100, 999)}"
        self.sala = obter_sala(self.sala_id)
        self.sala.adicionar_jogador(self)
        log_servidor.info("Cliente %s entrou na sala %s", self.usuario, self.sala_id)
        asyncio.create_task(self._pos_conexao())

    async def _pos_conexao(self) -> None:
        await self.sala.enviar_estado_inicial(self)
        await self.sala.broadcast_jogadores()
        await self.sala.broadcast_placar()
        await self.sala.broadcast(
            serializar(
                MSG_SYSTEM,
                texto=f"{self.usuario} entrou na sala.",
                tipo_sys="entrada",
            )
        )
        if not self.sala.rodada_atual and not (self.sala.reinicio_task and not self.sala.reinicio_task.done()):
            await self.sala.iniciar_rodada()

    async def on_message(self, message: str | bytes) -> None:
        if not message:
            return

        try:
            dados = desserializar(message)
        except json.JSONDecodeError:
            try:
                chat_message = ChatMessage.decodificar(message)
            except Exception as exc:
                log_servidor.error("Mensagem inválida recebida: %s", exc)
                return
            dados = {"tipo": MSG_CHAT, "texto": chat_message.conteudo}
        except Exception as exc:
            log_servidor.error("Erro ao desserializar mensagem: %s", exc)
            return

        tipo = dados.get("tipo", MSG_CHAT)
        
        if tipo == "pronto":
            await self.sala.registrar_pronto(self)
            return

        texto = str(dados.get("texto", "")).strip()
        if not texto:
            return

        if tipo in {MSG_CHAT, MSG_GUESS}:
            await self.sala.processar_palpite(self, texto)

    def on_close(self) -> None:
        if not hasattr(self, "sala"):
            return
        self.sala.remover_jogador(self)
        asyncio.create_task(self.sala.broadcast_jogadores())
        asyncio.create_task(self.sala.broadcast_placar())
        asyncio.create_task(
            self.sala.broadcast(
                serializar(
                    MSG_SYSTEM,
                    texto=f"{self.usuario} saiu da sala.",
                    tipo_sys="saida",
                )
            )
        )
        log_servidor.info("Cliente %s saiu da sala %s", self.usuario, self.sala_id)
        if not self.sala.conexoes and self.sala_id in salas:
            del salas[self.sala_id]


async def ler_terminal_global() -> None:
    while True:
        try:
            texto = await asyncio.to_thread(input, "> ")
        except EOFError:
            return
        except Exception as exc:
            log_servidor.error("Erro no terminal do servidor: %s", exc)
            return

        if texto.lower() == "sair":
            return
        if not texto.strip():
            continue

        mensagem = serializar(MSG_SYSTEM, texto=f"[Servidor] {texto}", tipo_sys="admin")
        for sala in list(salas.values()):
            await sala.broadcast(mensagem)
