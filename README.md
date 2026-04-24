# Adivinhe a Palavra com Emojis

Jogo multiplayer de adivinhação em tempo real inspirado em dinâmicas como Gartic, mas com um formato diferente: no lugar de desenho, a rodada mostra uma combinação de emojis que representa uma palavra, verbo, filme, série ou conceito.

Os jogadores entram em uma sala, enviam palpites pelo chat e disputam quem descobre a resposta primeiro. Quando um palpite chega perto, o sistema avisa. Quem acerta ganha pontos e uma nova rodada começa automaticamente.

## Stack

- Python
- Tornado
- WebSocket
- JavaScript
- HTML/CSS

## Como funciona

- Cada sala é isolada e mantém seu próprio estado de jogo
- O servidor escolhe um desafio com emojis e categoria
- Os jogadores enviam palpites em tempo real
- O backend detecta:
  - acerto exato
  - acerto ignorando artigos e acentos
  - palpite "quase certo"
- O placar é atualizado ao vivo
- Se ninguém acertar, o tempo acaba e a resposta é revelada

## Estrutura principal

- **`main.py`**: inicializa o Tornado e publica a interface web
- **`servidor.py`**: controla salas, rodadas, pontuação, dicas e WebSocket
- **`protocolo.py`**: define mensagens, serialização e verificação de palpites
- **`clientes/console.py`**: cliente simples de terminal para testes
- **`clientes/web/`**: interface web do jogo

## Executando

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o servidor:

```bash
python main.py
```

Abra no navegador:

```text
http://localhost:8080/
```

Para entrar direto em uma sala:

```text
http://localhost:8080/?sala=amigos
```

## Fluxo do jogo

1. O jogador informa nome e sala.
2. O servidor conecta o jogador ao WebSocket da sala.
3. A rodada mostra os emojis e a categoria.
4. Os palpites são enviados pelo próprio chat.
5. Ao acertar, o vencedor recebe pontos e a resposta é exibida.
6. Alguns segundos depois, começa a próxima rodada.

## Regras atuais

- Tempo por rodada: `60s`
- Pontuação por acerto: `30`
- Dicas automáticas durante a rodada
- Salas em memória, sem persistência
- Sem autenticação

## Observações

- O projeto depende de `tornado` para rodar o servidor
- Para testar com `pytest`, instale também as dependências de teste do seu ambiente
- As salas e pontuações são reiniciadas quando o servidor é encerrado

## Próximos passos sugeridos

- adicionar botão de iniciar/reiniciar rodada manualmente
- criar modo host da sala
- persistir ranking entre partidas
- aumentar o banco de desafios
- separar chat social de campo exclusivo de palpite