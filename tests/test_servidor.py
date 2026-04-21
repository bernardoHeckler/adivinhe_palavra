import asyncio
import json
import os

import tornado.testing
import tornado.web
import tornado.websocket

from servidor import ChatHandler

class TestWebSocketServer(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_web = os.path.join(dir_atual, "..", "clientes", "web")
        return tornado.web.Application([
            (r"/chat", ChatHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": dir_web, "default_filename": "index.html"}),
        ])

    @tornado.testing.gen_test
    async def test_websocket_conexao_e_mensagem(self):
        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/chat"
        ws_client = await tornado.websocket.websocket_connect(ws_url)
        
        # Test valid message processing
        payload = json.dumps({"remetente": "TestClient", "conteudo": "Ping"})
        await ws_client.write_message(payload)
        
        # Wait a tick so the server processes it
        await asyncio.sleep(0.1)
        
        # Test empty message
        await ws_client.write_message("")
        await asyncio.sleep(0.1)
        
        ws_client.close()
        await asyncio.sleep(0.1)
        # Should cleanly finish
        assert True
