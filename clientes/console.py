import asyncio
import json
import inspect
from logging import Logger

from tornado.websocket import WebSocketClientConnection, websocket_connect

from logger import configurar_logger, obter_logger
from protocolo import ChatMessage, desserializar

log_cliente: Logger = obter_logger("Cliente")


async def fechar_conexao(conexao: WebSocketClientConnection) -> None:
    resultado = conexao.close()
    if inspect.isawaitable(resultado):
        await resultado


async def receber_mensagens(conexao: WebSocketClientConnection) -> None:
    """Escutador full-time de mensagens recebidas pela rede."""
    while True:
        msg: str | bytes | None = await conexao.read_message()
        if msg is None:
            log_cliente.info("ConexÃ£o encerrada pelo servidor.")
            break

        try:
            dados = desserializar(msg)
        except Exception:
            msg_recebida = ChatMessage.decodificar(msg)
            obter_logger(msg_recebida.remetente).info(msg_recebida.conteudo)
            continue

        tipo = dados.get("tipo")
        if tipo == "chat":
            obter_logger(dados.get("usuario", "Sala")).info(dados.get("texto", ""))
        elif tipo == "system":
            obter_logger("Sistema").info(dados.get("texto", ""))
        elif tipo == "round_start":
            obter_logger("Jogo").info(
                f"Rodada {dados.get('rodada')}: {dados.get('emojis')} ({dados.get('categoria')})"
            )
        elif tipo == "round_end":
            obter_logger("Jogo").info(f"Fim da rodada. Resposta: {dados.get('resposta')}")
        else:
            obter_logger("Jogo").info(str(dados))


async def ler_terminal(conexao: WebSocketClientConnection) -> None:
    """Escutador full-time do terminal do teclado local do cliente."""
    while True:
        try:
            texto: str = await asyncio.to_thread(input, "> ")
            if texto.lower() == "sair":
                await fechar_conexao(conexao)
                break
            if texto.strip():
                await conexao.write_message(json.dumps({"tipo": "guess", "texto": texto}, ensure_ascii=False))
        except EOFError:
            await fechar_conexao(conexao)
            break
        except Exception as e:
            log_cliente.error(f"Erro no terminal do cliente: {e}")
            break


async def iniciar_cliente() -> None:
    url: str = "ws://localhost:8080/chat/ws?usuario=ClienteCLI&sala=default"
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
        log_cliente.error("NÃ£o foi possÃ­vel conectar ao servidor. O servidor estÃ¡ rodando?")
    except Exception as e:
        log_cliente.error(f"Erro na conexÃ£o com WebSocket: {e}")


if __name__ == "__main__":
    configurar_logger()
    asyncio.run(iniciar_cliente())
