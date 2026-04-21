import asyncio
from logging import Logger

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

import urllib.parse

from logger import obter_logger
from protocolo import ChatMessage

log_servidor: Logger = obter_logger("Servidor")

salas = {}

class ChatHandler(WebSocketHandler):
    entrada_ativa: bool

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self) -> None:
        query = urllib.parse.urlparse(self.request.uri).query
        parametros = urllib.parse.parse_qs(query)
        
        self.sala_id = parametros.get("sala", ["default"])[0]
        
        if self.sala_id not in salas:
            salas[self.sala_id] = set()
        
        salas[self.sala_id].add(self)
        
        log_servidor.info(f"Novo cliente conectado à sala '{self.sala_id}'")
        
        log_servidor.info("Conectado com um cliente WebSocket!")
        self.entrada_ativa = True
        # Inicia a leitura assíncrona do terminal - agenda na IOLoop
        # IOLoop.current().add_callback(self.ler_terminal)

    def on_message(self, message: str | bytes) -> None:
        if not message:
            return
        try: 
            msg_recebida: ChatMessage = ChatMessage.decodificar(message)
            obter_logger(msg_recebida.remetente).info(msg_recebida.conteudo)

            for connections in salas.get(self.sala_id, []):
                if connections is not self:
                    connections.write_message(message)
        except Exception as e:
            log_servidor.error(f"Erro ao processar mensagem: {e}")

    def on_close(self) -> None:
        self.entrada_ativa = False

        if hasattr(self, "sala_id") and self.sala_id in salas:
            salas[self.sala_id].discard(self)

            # limpa sala vazia
            if not salas[self.sala_id]:
                del salas[self.sala_id]

        log_servidor.info(f"Conexão encerrada na sala {getattr(self, 'sala_id', 'desconhecida')}")

async def ler_terminal_global():
    """ Rotina que lê o terminal do servidor de forma concorrente, sem matar o WebSocket """
    while True:
        try:
            texto: str = await asyncio.to_thread(input, "> ")
            
            if texto.lower() == 'sair':
                self.close()
                break
            if texto.strip():
                msg_envio: ChatMessage = ChatMessage(remetente="Servidor", conteudo=texto)
                mensagem = msg_envio.codificar()

                for conexoes in salas.values():
                    for connections in list(conexoes):
                        try:
                            await connections.write_message(mensagem)
                        except:
                            conexoes.discard(connections)
        
        except Exception as e:
            log_servidor.error(f"Erro no terminal do servidor: {e}")
            break
