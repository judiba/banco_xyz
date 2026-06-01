import logging
from fastapi.testclient import TestClient
from backend.main import app
from backend.app_config.logging import correlation_id_var


def test_correlation_id_generated_automatically():
    """
    Testa se o middleware gera automaticamente um Correlation ID (UUID v4)
    e calcula a latência para requisições que não o enviam originalmente.
    """
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Correlation-Id" in response.headers
    assert "X-Process-Time-Ms" in response.headers

    # Valida se o ID gerado possui o tamanho típico de UUID v4
    corr_id = response.headers["X-Correlation-Id"]
    assert len(corr_id) == 36
    assert corr_id.count("-") == 4


def test_correlation_id_propagated_from_request():
    """
    Testa se o middleware preserva e propaga corretamente um Correlation ID
    fornecido pelo cliente no header 'X-Correlation-Id'.
    """
    client = TestClient(app)
    custom_id = "test-correlation-id-12345"
    response = client.get("/", headers={"X-Correlation-Id": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == custom_id
    assert "X-Process-Time-Ms" in response.headers


def test_logging_context_contains_correlation_id(caplog):
    """
    Testa se a ContextVar é atualizada durante o ciclo de vida da requisição
    e se o CorrelationIdFilter injeta o ID correto nos logs.
    """
    client = TestClient(app)
    custom_id = "log-trace-id-999"

    # Captura logs de nível INFO ou superior
    with caplog.at_level(logging.INFO):
        response = client.get("/", headers={"X-Correlation-Id": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Correlation-Id"] == custom_id

    # Garante que pelo menos um log de request_tracing foi registrado contendo o Correlation ID
    tracing_logs = [record for record in caplog.records if record.name == "request_tracing"]
    assert len(tracing_logs) > 0

    for record in tracing_logs:
        # O filtro customizado deve ter injetado o correlation_id no objeto record
        assert getattr(record, "correlation_id", None) == custom_id


def test_context_var_is_cleaned_after_request():
    """
    Testa se o contextvar é devidamente resetado/desalocado após a conclusão da requisição,
    evitando vazamento de IDs (leak) para threads ou tarefas paralelas.
    """
    client = TestClient(app)
    client.get("/", headers={"X-Correlation-Id": "leak-prevention-test"})

    # Fora do escopo da requisição, o valor default do contextvar deve ser restabelecido
    assert correlation_id_var.get() == "-"
