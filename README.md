# Adivinhe a Palavra com Emojis

Projeto acadêmico de um jogo multiplayer em tempo real feito para estudar comunicação cliente-servidor com WebSocket.

A proposta do projeto é usar uma dinâmica simples de adivinhação por emojis para praticar conceitos como:

- conexão persistente entre cliente e servidor
- troca de mensagens em tempo real
- gerenciamento de salas
- sincronização de estado entre múltiplos jogadores
- atualização de interface a partir de eventos do backend

## Objetivo acadêmico

Mais do que apenas entregar um jogo, este projeto foi construído para apoiar o aprendizado de WebSockets em um contexto prático.

Com ele, é possível observar:

- como o servidor mantém conexões abertas com vários clientes ao mesmo tempo
- como eventos de jogo são enviados em tempo real para todos os jogadores da sala
- como o backend controla rodadas, pontuação e reinício de partidas
- como o frontend React reage às mensagens recebidas pelo socket

## Como o jogo funciona

- cada sala possui seu próprio estado
- o servidor escolhe um desafio com emojis e categoria
- os jogadores enviam palpites pelo chat em tempo real
- em sala com 1 jogador, acertou e a próxima rodada começa logo depois
- em sala com 2 ou mais jogadores, a rodada continua até o tempo acabar
- a pontuação depende da ordem de acerto na rodada
- a partida termina quando alguém atinge `300` pontos

## Stack utilizada

- Python
- Tornado
- WebSocket
- React
- Vite

## Estrutura principal

- `main.py`: inicia o servidor Tornado e publica o frontend buildado
- `servidor.py`: controla salas, rodadas, regras de pontuação e WebSocket
- `protocolo.py`: define serialização das mensagens e validação dos palpites
- `clientes/web/`: frontend React do jogo
- `clientes/console.py`: cliente simples de terminal para testes
- `tests/`: testes automatizados

## Passo a passo para rodar o projeto

### 1. Entrar na pasta do projeto

```bash
cd /caminho/para/adivinhe_palavra
```

### 2. Criar e ativar um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências do backend

```bash
pip install -r requirements.txt
```

### 4. Instalar dependências do frontend

```bash
cd clientes/web
npm install
```

### 5. Gerar o build do frontend

O servidor Python serve os arquivos estáticos a partir de `clientes/web/dist`, então esse build precisa existir antes da execução.

```bash
npm run build
cd ../..
```

### 6. Iniciar o servidor

```bash
python3 main.py
```

Se aparecer `OSError: [Errno 98] Address already in use`, a porta `8080` já está ocupada. Para liberar:

```bash
fuser -k 8080/tcp
```

### 7. Abrir no navegador

```text
http://localhost:8080/
```

Para entrar direto em uma sala específica:

```text
http://localhost:8080/?sala=amigos
```

## Passo a passo para desenvolvimento

Se quiser desenvolver o frontend com recarga automática:

### Terminal 1: backend

```bash
cd /caminho/para/adivinhe_palavra
source .venv/bin/activate
python3 main.py
```

### Terminal 2: frontend

```bash
cd /caminho/para/adivinhe_palavra/clientes/web
npm install
npm run dev
```

O Vite sobe em:

```text
http://localhost:5173/
```

Nesse modo, o frontend se conecta automaticamente ao backend em `localhost:8080`.

## Regras atuais da partida

- tempo por rodada: `60` segundos
- intervalo entre rodadas: `4` segundos
- pontuação por ordem de acerto: `30`, `20`, `15`, `10` e depois `5`
- meta para vencer a partida: `300` pontos
- salas e pontuações ficam somente em memória

## Testes

Para rodar os testes automatizados:

```bash
pytest
```

Ou apenas os testes do servidor:

```bash
pytest tests/test_servidor.py
```

## Observações

- o servidor principal roda na porta `8080`
- o frontend usa `vite@5`, compatível com `Node 18`
- o build do frontend precisa existir para o Tornado servir a interface final
- como as salas ficam em memória, tudo é perdido ao reiniciar o servidor
