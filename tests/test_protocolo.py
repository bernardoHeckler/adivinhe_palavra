import pytest
from protocolo import ChatMessage

def test_codificar():
    msg = ChatMessage(remetente="Teste", conteudo="Olá")
    codificado = msg.codificar()
    assert '"remetente": "Teste"' in codificado
    assert '"conteudo": "Ol\\u00e1"' in codificado or '"conteudo": "Olá"' in codificado

def test_decodificar_string():
    payload = '{"remetente": "A", "conteudo": "B"}'
    msg = ChatMessage.decodificar(payload)
    assert msg.remetente == "A"
    assert msg.conteudo == "B"

def test_decodificar_bytes():
    payload = b'{"remetente": "A", "conteudo": "B"}'
    msg = ChatMessage.decodificar(payload)
    assert msg.remetente == "A"
    assert msg.conteudo == "B"
