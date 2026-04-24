import asyncio
import json
import os

import tornado.testing
import tornado.web
import tornado.websocket

from servidor import ChatHandler, salas


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
