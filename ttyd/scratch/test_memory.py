"""
Teste de integração da Memória DynamoDB (DEV_OFFLINE).
Execute com: DEV_OFFLINE=true python scratch/test_memory.py
"""

import os

os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("DEV_OFFLINE", "true")

from backend.memory.memory_store import (
    build_session_id,
    save_message,
    get_history,
    clear_session,
    history_to_prompt,
)
from backend.memory.memory_writer import save_turn
from backend.memory.memory_retriever import load_memory_context


def test_session_id():
    sid = build_session_id("record-tv", "user123")
    assert "record-tv" in sid
    assert "user123" in sid
    print(f"✅ session_id gerado: {sid}")


def test_save_and_get():
    sid = build_session_id("test-org", "test-user")
    clear_session(sid)

    save_message(sid, "user", "Qual o total de vendas?")
    save_message(sid, "assistant", "As vendas totalizaram R$ 1.2M no trimestre.")

    history = get_history(sid)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    print(f"✅ Histórico salvo e recuperado: {len(history)} mensagem(ns)")


def test_history_to_prompt():
    sid = build_session_id("test-org", "test-user")
    history = get_history(sid)
    prompt = history_to_prompt(history)
    assert "Usuário" in prompt
    assert "Assistente" in prompt
    print("✅ Histórico convertido para prompt LLM")
    print(f"   Prévia:\n{prompt[:150]}...")


def test_save_turn():
    sid = build_session_id("test-org", "turno-user")
    clear_session(sid)

    save_turn(sid, "Quais são os KPIs do mês?", "Os principais KPIs são audiência, receita e NPS.")

    history = get_history(sid)
    assert len(history) == 2, f"Esperava 2, obteve {len(history)}"
    print("✅ Turno salvo via memory_writer")


def test_short_message_ignored():
    sid = build_session_id("test-org", "short-user")
    clear_session(sid)
    save_turn(sid, "ok", "Resposta.")  # mensagem curta — deve ser ignorada
    history = get_history(sid)
    assert len(history) == 0, "Mensagens curtas não devem ser salvas"
    print("✅ Mensagem curta (<10 chars) corretamente ignorada")


def test_load_memory_context():
    sid = build_session_id("test-org", "ctx-user")
    clear_session(sid)
    save_turn(sid, "Quais são os dados de audiência?", "A audiência média foi de 8.5 pontos.")
    ctx = load_memory_context(sid)
    assert "Histórico" in ctx
    assert "audiência" in ctx
    print("✅ load_memory_context retorna histórico injetável no prompt")


def test_clear_session():
    sid = build_session_id("test-org", "clear-user")
    save_message(sid, "user", "Mensagem de teste para limpeza.")
    clear_session(sid)
    history = get_history(sid)
    assert len(history) == 0
    print("✅ Sessão limpa com sucesso")


if __name__ == "__main__":
    print("\n🔬 Testando Memória DynamoDB (modo DEV_OFFLINE)\n")
    test_session_id()
    test_save_and_get()
    test_history_to_prompt()
    test_save_turn()
    test_short_message_ignored()
    test_load_memory_context()
    test_clear_session()
    print("\n✅ Todos os testes de memória passaram!\n")
