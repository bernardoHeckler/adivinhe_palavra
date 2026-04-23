import os
from logging import Logger

from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler, RequestHandler

from logger import configurar_logger, obter_logger
from servidor import ChatHandler, ler_terminal_global, obter_ip_local

log_servidor: Logger = obter_logger("Servidor")


class IpHandler(RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.write({"ip": obter_ip_local()})

def make_app() -> Application:
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_web = os.path.join(dir_atual, "clientes", "web", "dist")
    return Application(
        [
            (r"/api/ip", IpHandler),
            (r"/chat/ws", ChatHandler),
            (r"/(.*)", StaticFileHandler, {"path": dir_web, "default_filename": "index.html"}),
        ],
        debug=True,
    )


def iniciar_servidor() -> None:
    app = make_app()
    porta = 8081
    app.listen(porta)
    log_servidor.info("Servidor iniciado em http://localhost:%s", porta)
    log_servidor.info("WebSocket disponível em ws://localhost:%s/chat/ws", porta)
    IOLoop.current().add_callback(ler_terminal_global)
    IOLoop.current().start()


if __name__ == "__main__":
    configurar_logger()
    iniciar_servidor()
