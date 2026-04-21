import logging
from logger import configurar_logger, obter_logger

def test_configurar_logger():
    configurar_logger()
    logger = logging.getLogger()
    assert logger.level == logging.INFO

def test_obter_logger():
    logger = obter_logger("TesteLoggerZ")
    assert logger.name == "TesteLoggerZ"
