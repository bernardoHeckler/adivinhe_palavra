import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock

import tornado.testing
import tornado.web
import tornado.websocket

from servidor import ChatHandler, SalaJogo, salas


class ConexaoFalsa:
    def __init__(self, usuario: str):
        self.usuario = usuario
        self.write_message = AsyncMock()


class TestWebSocketServer(tornado.testing.AsyncHTTPTestCase):
    def setUp(self):
        salas.clear()
        super().setUp()

    def get_app(self):
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_web = os.path.join(dir_atual, "..", "clientes", "web")
        return tornado.web.Application([
            (r"/chat/ws", ChatHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": dir_web, "default_filename": "index.html"}),
        ])

    @tornado.testing.gen_test
    async def test_websocket_conexao_e_mensagem(self):
        ws_url = f"ws://localhost:{self.get_http_port()}/chat/ws?sala=teste&usuario=Alice"
        ws_client = await tornado.websocket.websocket_connect(ws_url)

        recebeu_rodada = False
        for _ in range(5):
            mensagem = await ws_client.read_message()
            if mensagem is None:
                break
            dados = json.loads(mensagem)
            if dados["tipo"] == "round_start":
                recebeu_rodada = True
                break

        assert recebeu_rodada is True

        await ws_client.write_message(json.dumps({"tipo": "guess", "texto": "batman"}))
        recebeu_resposta = False

        for _ in range(5):
            mensagem = await ws_client.read_message()
            if mensagem is None:
                break
            dados = json.loads(mensagem)
            if dados["tipo"] in {"chat", "round_end"}:
                recebeu_resposta = True
                break

        assert recebeu_resposta is True

        await ws_client.write_message("")
        await asyncio.sleep(0.1)

        ws_client.close()
        await asyncio.sleep(0.1)
        assert True


class TestSalaJogoPontuacao(tornado.testing.AsyncTestCase):
    def setUp(self):
        salas.clear()
        super().setUp()

    @tornado.testing.gen_test
    async def test_jogador_unico_acerta_e_rodada_reinicia(self):
        sala = SalaJogo("solo")
        conexao = ConexaoFalsa("Alice")
        sala.adicionar_jogador(conexao)
        sala.agendar_proxima_rodada = MagicMock()
        sala.broadcast = AsyncMock()
        sala.broadcast_placar = AsyncMock()
        sala.rodada_atual = {
            "desafio": {"resposta": "batman", "categoria": "Filme", "emojis": "🦇", "dicas": []},
            "inicio": 0,
            "dicas_enviadas": 0,
            "acertadores": set(),
            "ordem_acertos": [],
        }

        await sala.processar_palpite(conexao, "batman")

        assert sala.pontuacoes["Alice"] == 30
        assert sala.rodada_atual is None
        sala.agendar_proxima_rodada.assert_called_once()
        sala.broadcast.assert_any_call(
            json.dumps(
                {
                    "tipo": "round_end",
                    "motivo": "acerto",
                    "vencedor": "Alice",
                    "resposta": "batman",
                    "placar": [{"usuario": "Alice", "pontos": 30}],
                },
                ensure_ascii=False,
            )
        )

    @tornado.testing.gen_test
    async def test_multiplayer_mantem_rodada_ate_tempo_e_pontua_por_ordem(self):
        sala = SalaJogo("grupo")
        alice = ConexaoFalsa("Alice")
        bob = ConexaoFalsa("Bob")
        sala.adicionar_jogador(alice)
        sala.adicionar_jogador(bob)
        sala.agendar_proxima_rodada = MagicMock()
        sala.broadcast = AsyncMock()
        sala.broadcast_placar = AsyncMock()
        sala.rodada_atual = {
            "desafio": {"resposta": "batman", "categoria": "Filme", "emojis": "🦇", "dicas": []},
            "inicio": 0,
            "dicas_enviadas": 0,
            "acertadores": set(),
            "ordem_acertos": [],
        }

        await sala.processar_palpite(alice, "batman")
        await sala.processar_palpite(bob, "batman")

        assert sala.pontuacoes["Alice"] == 30
        assert sala.pontuacoes["Bob"] == 20
        assert sala.rodada_atual is not None
        assert sala.rodada_atual["ordem_acertos"] == ["Alice", "Bob"]
        sala.agendar_proxima_rodada.assert_not_called()

        mensagens = [call.args[0] for call in sala.broadcast.await_args_list]
        assert any("Alice acertou em 1º lugar e ganhou 30 pontos" in mensagem for mensagem in mensagens)
        assert any("Bob acertou em 2º lugar e ganhou 20 pontos" in mensagem for mensagem in mensagens)
        assert not any('"tipo": "round_end"' in mensagem for mensagem in mensagens)
