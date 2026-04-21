# WebSocket Chat (Tornado Assíncrono)

A mesma base didática do chat interativo, mas agora utilizando o protocolo **WebSocket** em conjunto com o framework de alta performance **Tornado**! 

Ele introduz o modelo de **Duplex Completo (Assíncrono)**; o que significa que diferentemente do modelo sequencial travado, **ninguém precisa aguardar pela resposta do outro**. O recebimento de rede e o console local rodam paralelamente sem bloqueios.
Por ser um sistema em tempo real puro, o servidor não armazena mensagens: elas são apenas transmitidas entre os clientes conectados naquele momento.
Além disso, o sistema agora suporta **múltiplas salas de chat simultâneas**, permitindo que diferentes grupos de usuários se comuniquem de forma isolada dentro da mesma aplicação.

## 📌 Arquitetura

O chat agora é gerido num formato orientado a eventos no clássico Loop (`IOLoop`):
- O **Tornado Web** (`tornado.web.Application`) instanciou um *Handler* persistente (`/chat`) na especificação WebSocket.
- O Terminal do servidor e do cliente rodam uma *coroutine* poderosa (`asyncio.to_thread`) que lê o teclado simultaneamente à placa de rede.
- O payload de protocolo agora codifica os bytes numa `String` limpa em memória ao invés de bytes transientes.
- O servidor mantém um gerenciamento em memória das conexões organizadas por sala (`dict[sala] = conexões`), garantindo o isolamento das mensagens.

## 📂 Estrutura de Arquivos

* **`servidor.py`**: O arquivo de backend na raiz que Roda o servidor WebSocket Tornado.
* **`clientes/console.py`**: O cliente Python Terminal em si usando `websocket_connect()`.
* **`clientes/web/`**: A bela Interface Gráfica Glassmorphism provida pelo próprio Tornado no Root URL.
* **`main.py`**: Arquivo responsável por inicializar a aplicação Tornado e configurar as rotas.
* **`protocolo.py`**: Define a estrutura das mensagens e sua serialização/desserialização.

## 🚀 Como Executar

### 1. Instale o Tornado
Se ainda não possuir, instale o único requerimento mapeado no ecossistema atual:
```bash
pip install -r requirements.txt
```

### 2. Inicie o Servidor e o Client
Com a nova arquitetura de pacotes e a presença do `__init__.py`, executamos a partir da raiz do repositório garantindo que as bibliotecas cruzem de forma correta (`-m`).

**Terminal 1:**
```bash
python main.py
```
**Terminal 2:** Abra o navegador em `http://localhost:8080/` OU execute a CLI local:
```bash
python -m clientes.console
```

### 3. Após abrir o navegador
Você pode acessar salas diferentes diretamente pela URL:

`http://localhost:8080/?sala=abc`

Caso nenhum parâmetro seja informado, o sistema conecta automaticamente na sala `default`.

## 💬 Funcionamento das Salas

Cada conexão WebSocket é associada a uma sala através de um parâmetro de query (`?sala=nome`).

- Usuários na mesma sala recebem mensagens entre si
- Usuários em salas diferentes são totalmente isolados
- As salas são criadas dinamicamente conforme a conexão dos clientes

> ⚠️ O endpoint `/chat/ws` é exclusivo para WebSocket e não deve ser acessado diretamente pelo navegador

## 🧪 Validando a Qualidade (Testes)

O framework de testes está suportado via `pytest` com Mocks de terminal de rede. O sistema cobre todos os eventos base (Conexão, Decodificação e Mensageria Assíncrona).

Para executa-los localmente:
```bash
pip install pytest pytest-cov pytest-asyncio
pytest tests/ --cov=backend --cov=clientes.console
```

## ⚠️ Observações

- As salas são mantidas em memória (não persistem após reinício do servidor)
- As mensagens não são armazenadas (não existe histórico de chat)
- O sistema não possui autenticação (qualquer usuário pode entrar em qualquer sala)
- O chat funciona apenas em tempo real (as mensagens existem apenas durante a conexão ativa)

*A GitHub Action implementada atestará o Deploy Continuamente após cada envio `Push` pro main.*

## 🚧 Melhorias Futuras

- Persistência de mensagens (histórico de chat)
- Autenticação de usuários
- Escalabilidade com Redis