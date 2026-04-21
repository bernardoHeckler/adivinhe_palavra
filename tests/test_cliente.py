import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from clientes.console import ler_terminal, receber_mensagens

@pytest.mark.asyncio
async def test_receber_mensagens():
    conexao_mock = AsyncMock()
    conexao_mock.read_message.side_effect = ['{"remetente": "S", "conteudo": "Oi"}', None]
    
    await receber_mensagens(conexao_mock)
    assert conexao_mock.read_message.call_count == 2

@pytest.mark.asyncio
async def test_ler_terminal_vazio_sair(caplog):
    conexao_mock = AsyncMock()
    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_input:
        # Testa espaco em branco seguido de sair
        mock_input.side_effect = ['   ', 'sair']
        await ler_terminal(conexao_mock)
        conexao_mock.close.assert_called_once()
        conexao_mock.write_message.assert_not_called()

@pytest.mark.asyncio
async def test_ler_terminal_mensagem_valida():
    conexao_mock = AsyncMock()
    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_input:
        mock_input.side_effect = ['teste veloz', 'sair']
        await ler_terminal(conexao_mock)
        conexao_mock.write_message.assert_called_once()
        conexao_mock.close.assert_called_once()

@pytest.mark.asyncio
async def test_ler_terminal_eoferror():
    conexao_mock = AsyncMock()
    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_input:
        mock_input.side_effect = EOFError()
        await ler_terminal(conexao_mock)
        conexao_mock.close.assert_called_once()
        
@pytest.mark.asyncio
async def test_ler_terminal_generic_exception():
    conexao_mock = AsyncMock()
    with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_input:
        mock_input.side_effect = Exception("Erro critico")
        await ler_terminal(conexao_mock)
        # Exception handler inside the module logs it and breaks cleanly.
        assert True
