import json
import unicodedata
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True)
class ChatMessage:
    remetente: str
    conteudo: str

    def codificar(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def decodificar(dados: str | bytes) -> "ChatMessage":
        texto = dados.decode("utf-8") if isinstance(dados, bytes) else dados
        dicionario = json.loads(texto)
        return ChatMessage(
            remetente=dicionario.get("remetente", "Anônimo"),
            conteudo=dicionario.get("conteudo", ""),
        )


MSG_CHAT = "chat"
MSG_SYSTEM = "system"
MSG_GUESS = "guess"
MSG_GAME_STATE = "game_state"
MSG_ROUND_START = "round_start"
MSG_ROUND_END = "round_end"
MSG_MATCH_END = "match_end"
MSG_SCOREBOARD = "scoreboard"
MSG_PLAYER_LIST = "player_list"


DESAFIOS = [
    {"emojis": "🦁👑🌍", "resposta": "o rei leão", "categoria": "Filme", "dicas": ["animação", "disney"]},
    {"emojis": "🕷️🧑‍🦱🏙️", "resposta": "homem aranha", "categoria": "Filme", "dicas": ["super-herói", "marvel"]},
    {"emojis": "🧊❄️👸", "resposta": "frozen", "categoria": "Filme", "dicas": ["irmãs", "disney"]},
    {"emojis": "🐟🔍🌊", "resposta": "procurando nemo", "categoria": "Filme", "dicas": ["animação", "oceano"]},
    {"emojis": "🚀👨‍🚀🌌", "resposta": "interestelar", "categoria": "Filme", "dicas": ["espaço", "tempo"]},
    {"emojis": "🧙‍♂️💍🌋", "resposta": "o senhor dos anéis", "categoria": "Filme", "dicas": ["fantasia", "trilogia"]},
    {"emojis": "🦇🌃🕵️", "resposta": "batman", "categoria": "Filme", "dicas": ["dc", "gotham"]},
    {"emojis": "🦖🏞️😱", "resposta": "jurassic park", "categoria": "Filme", "dicas": ["dinossauros", "parque"]},
    {"emojis": "🚂⏰🔮", "resposta": "de volta para o futuro", "categoria": "Filme", "dicas": ["viagem no tempo", "clássico"]},
    {"emojis": "🐭👨‍🍳🍽️", "resposta": "ratatouille", "categoria": "Filme", "dicas": ["cozinha", "rato"]},
    {"emojis": "💀⚗️🔵", "resposta": "breaking bad", "categoria": "Série", "dicas": ["professor", "drama"]},
    {"emojis": "🐉🗡️👑", "resposta": "game of thrones", "categoria": "Série", "dicas": ["fantasia", "trono"]},
    {"emojis": "👨‍👩‍👧‍👦🛋️☕", "resposta": "friends", "categoria": "Série", "dicas": ["comédia", "nova york"]},
    {"emojis": "🏝️✈️🔁", "resposta": "lost", "categoria": "Série", "dicas": ["ilha", "mistério"]},
    {"emojis": "🧟‍♂️🔫🌆", "resposta": "the walking dead", "categoria": "Série", "dicas": ["zumbi", "apocalipse"]},
    {"emojis": "🔍🧠🎻", "resposta": "sherlock", "categoria": "Série", "dicas": ["detetive", "watson"]},
    {"emojis": "👨‍💼📊😐", "resposta": "the office", "categoria": "Série", "dicas": ["trabalho", "comédia"]},
    {"emojis": "🌵🤠⭐", "resposta": "mandalorian", "categoria": "Série", "dicas": ["star wars", "grogu"]},
    {"emojis": "🦑🎮💰", "resposta": "round 6", "categoria": "Série", "dicas": ["coreano", "sobrevivência"]},
    {"emojis": "🏃‍♂️💨🚪", "resposta": "fugir", "categoria": "Verbo", "dicas": ["escapar", "correr"]},
    {"emojis": "😴💤🛏️", "resposta": "dormir", "categoria": "Verbo", "dicas": ["descanso", "noite"]},
    {"emojis": "🍳🧑‍🍳🔥", "resposta": "cozinhar", "categoria": "Verbo", "dicas": ["fogão", "comida"]},
    {"emojis": "✈️🌍🧳", "resposta": "viajar", "categoria": "Verbo", "dicas": ["turismo", "mundo"]},
    {"emojis": "📚👀🧠", "resposta": "estudar", "categoria": "Verbo", "dicas": ["escola", "aprender"]},
    {"emojis": "❤️😍💏", "resposta": "se apaixonar", "categoria": "Verbo", "dicas": ["amor", "romance"]},
    {"emojis": "🎤🎵🎶", "resposta": "cantar", "categoria": "Verbo", "dicas": ["voz", "música"]},
    {"emojis": "⚽🥅🏆", "resposta": "jogar futebol", "categoria": "Verbo", "dicas": ["esporte", "gol"]},
    {"emojis": "🗼🥖🍷", "resposta": "paris", "categoria": "Lugar", "dicas": ["frança", "cidade"]},
    {"emojis": "🏖️☀️🌴", "resposta": "praia", "categoria": "Lugar", "dicas": ["areia", "verão"]},
    {"emojis": "🎡🎢🎠", "resposta": "parque de diversões", "categoria": "Lugar", "dicas": ["brinquedos", "lazer"]},
]


def _remover_acentos(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(char for char in texto if unicodedata.category(char) != "Mn")


def normalizar_resposta(texto: str) -> str:
    texto = _remover_acentos(texto)
    termos_ignorados = {"o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das"}
    partes = [parte for parte in texto.replace("-", " ").split() if parte not in termos_ignorados]
    return " ".join(partes)


def verificar_palpite(palpite: str, resposta: str) -> tuple[bool, bool]:
    palpite_normalizado = normalizar_resposta(palpite)
    resposta_normalizada = normalizar_resposta(resposta)

    if not palpite_normalizado:
        return False, False

    if palpite_normalizado == resposta_normalizada:
        return True, False

    similaridade = SequenceMatcher(None, palpite_normalizado, resposta_normalizada).ratio()
    if similaridade >= 0.72:
        return False, True

    palavras_resposta = {palavra for palavra in resposta_normalizada.split() if len(palavra) > 3}
    palavras_palpite = {palavra for palavra in palpite_normalizado.split() if len(palavra) > 3}
    if palavras_resposta and palavras_palpite:
        intersecao = len(palavras_resposta & palavras_palpite)
        if intersecao / len(palavras_resposta) >= 0.6:
            return False, True

    return False, False


def serializar(tipo: str, **dados) -> str:
    return json.dumps({"tipo": tipo, **dados}, ensure_ascii=False)


def desserializar(raw: str | bytes) -> dict:
    texto = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    return json.loads(texto)
