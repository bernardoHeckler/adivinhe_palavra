import os
from logging import Logger

from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler

from logger import configurar_logger, obter_logger
from servidor import ChatHandler, ler_terminal_global

log_servidor: Logger = obter_logger("Servidor")


def make_app() -> Application:
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_web = os.path.join(dir_atual, "clientes", "web")
    return Application(
        [
            (r"/chat/ws", ChatHandler),
            (r"/(.*)", StaticFileHandler, {"path": dir_web, "default_filename": "index.html"}),
        ],
        debug=True,
    )


def iniciar_servidor() -> None:
    app = make_app()
    porta = 8080
    app.listen(porta)
    log_servidor.info("Servidor iniciado em http://localhost:%s", porta)
    log_servidor.info("WebSocket disponível em ws://localhost:%s/chat/ws", porta)
    IOLoop.current().add_callback(ler_terminal_global)
    IOLoop.current().start()


if __name__ == "__main__":
    configurar_logger()
    iniciar_servidor()
