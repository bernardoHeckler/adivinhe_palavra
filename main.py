import os
import subprocess
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

def preparar_frontend() -> None:
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_web = os.path.join(dir_atual, "clientes", "web")
    
    log_servidor.info("Preparando frontend: instalando dependências (npm install)...")
    try:
        # shell=True é recomendado no Windows para comandos como npm
        subprocess.run(["npm", "install"], cwd=dir_web, check=True, shell=True)
        
        log_servidor.info("Preparando frontend: construindo build (npm run build)...")
        subprocess.run(["npm", "run", "build"], cwd=dir_web, check=True, shell=True)
        
        log_servidor.info("Frontend preparado com sucesso!")
    except subprocess.CalledProcessError as e:
        log_servidor.error("Erro ao preparar o frontend: %s", e)
    except FileNotFoundError:
        log_servidor.error("NPM não encontrado. Certifique-se de ter o Node.js instalado.")

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
    preparar_frontend()
    iniciar_servidor()
