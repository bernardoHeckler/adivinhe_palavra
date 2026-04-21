from protocolo import ChatMessage, desserializar, serializar, verificar_palpite


def test_codificar():
    msg = ChatMessage(remetente="Teste", conteudo="OlÃ¡")
    codificado = msg.codificar()
    assert '"remetente": "Teste"' in codificado
    assert '"conteudo": "OlÃ¡"' in codificado or '"conteudo": "Ol\\u00e1"' in codificado


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


def test_serializar_e_desserializar():
    payload = serializar("guess", texto="batman")
    dados = desserializar(payload)
    assert dados["tipo"] == "guess"
    assert dados["texto"] == "batman"


def test_verificar_palpite_ignora_artigo_e_acentos():
    acertou, quase = verificar_palpite("rei leao", "o rei leão")
    assert acertou is True
    assert quase is False


def test_verificar_palpite_quase_certo():
    acertou, quase = verificar_palpite("jurrasic park", "jurassic park")
    assert acertou is False
    assert quase is True
