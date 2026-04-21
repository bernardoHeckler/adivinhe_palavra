import asyncio
from logging import Logger

from tornado.websocket import WebSocketClientConnection, websocket_connect

from logger import configurar_logger, obter_logger
from protocolo import ChatMessage

log_cliente: Logger = obter_logger("Cliente")

async def receber_mensagens(conexao: WebSocketClientConnection) -> None:
    """Escutador full-time de mensagens recebidas pela rede."""
    while True:
        msg: str | bytes | None = await conexao.read_message()
        if msg is None:
            log_cliente.info("Conexão encerrada pelo servidor.")
            break
        msg_recebida = ChatMessage.decodificar(msg)
        obter_logger(msg_recebida.remetente).info(msg_recebida.conteudo)

async def ler_terminal(conexao: WebSocketClientConnection) -> None:
    """Escutador full-time do terminal do teclado local do cliente."""
    while True:
        try:
            texto: str = await asyncio.to_thread(input, "> ")
            if texto.lower() == 'sair':
                conexao.close()
                break
            if texto.strip():
                msg_envio = ChatMessage(remetente="Cliente", conteudo=texto)
                await conexao.write_message(msg_envio.codificar())
        except EOFError:
            conexao.close()
            break
        except Exception as e:
            log_cliente.error(f"Erro no terminal do cliente: {e}")
            break

async def iniciar_cliente() -> None:
    url: str = "ws://localhost:8080/chat"
    try:
        conexao: WebSocketClientConnection = await websocket_connect(url)
        log_cliente.info(f"Conectado ao servidor {url}! (Digite 'sair' para encerrar)")

        tarefa_recv: asyncio.Task[None] = asyncio.create_task(receber_mensagens(conexao))
        tarefa_envio: asyncio.Task[None] = asyncio.create_task(ler_terminal(conexao))

        await asyncio.wait(
            [tarefa_recv, tarefa_envio],
            return_when=asyncio.FIRST_COMPLETED
        )
    except ConnectionRefusedError:
        log_cliente.error("Não foi possível conectar ao servidor. O servidor está rodando?")
    except Exception as e:
        log_cliente.error(f"Erro na conexão com WebSocket: {e}")

if __name__ == "__main__":
    configurar_logger()
    asyncio.run(iniciar_cliente())
