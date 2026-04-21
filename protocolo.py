import json
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class ChatMessage:
    remetente: str
    conteudo: str

    def codificar(self) -> str:
        """Codifica a mensagem para string JSON (WebSockets operam nativamente com texto)."""
        return json.dumps(asdict(self))

    @staticmethod
    def decodificar(dados: str | bytes) -> 'ChatMessage':
        """Decodifica o payload JSON logando-o seguramente para um objeto ChatMessage."""
        texto = dados.decode('utf-8') if isinstance(dados, bytes) else dados
        dicionario = json.loads(texto)
        return ChatMessage(
                remetente=dicionario.get("remetente"),
                conteudo=dicionario.get("conteudo")
)
