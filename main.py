import os
from logging import Logger

from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler

from logger import configurar_logger, obter_logger
from servidor import ChatHandler, ler_terminal_global

log_servidor: Logger = obter_logger("Servidor")

def iniciar_servidor() -> None:
    dir_atual: str = os.path.dirname(os.path.abspath(__file__))
    dir_web: str = os.path.join(dir_atual, "clientes", "web")
    
    app: Application = Application([
        (r"/chat/ws", ChatHandler),
        (r"/(.*)", StaticFileHandler, {"path": dir_web, "default_filename": "index.html"}),
    ])
    porta: int = 8080
    app.listen(porta)
    log_servidor.info(f"Escutando porta {porta} em ws://localhost:{porta}/chat")
    log_servidor.info(f"🚀 Interface Web GUI rodando em http://localhost:{porta}")
    
    IOLoop.current().add_callback(ler_terminal_global)
    
    IOLoop.current().start()

if __name__ == "__main__":
    configurar_logger()
    iniciar_servidor()
