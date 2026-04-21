import logging

def configurar_logger() -> None:
    """Configura o logger global com o formato [HORARIO] [TIPO] Mensagem."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] %(message)s',
        datefmt='%H:%M:%S',
        force=True
    )

def obter_logger(nome: str) -> logging.Logger:
    """Retorna um logger configurado com o nome (TIPO) especificado."""
    return logging.getLogger(nome)
