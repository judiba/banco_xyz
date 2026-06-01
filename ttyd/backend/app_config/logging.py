import contextvars
import logging
import sys
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ContextVar thread/coroutine-safe para guardar o Correlation ID da transação ativa
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default="-"
)


class CorrelationIdFilter(logging.Filter):
    """
    Filtro de log customizado que extrai o Correlation ID ativo do contextvars
    e o injeta no registro de log para exibição estruturada.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get()
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configuração global e estruturada de logging do projeto TTYD (LEVEL 19).
    Injeta o CorrelationIdFilter no root logger para rastreabilidade ponta a ponta.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Limpa handlers pré-existentes para evitar duplicação de saídas
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Handler padrão direcionando logs para stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)

    # Injeção do filtro de correlação
    stream_handler.addFilter(CorrelationIdFilter())

    # Formato premium incluindo o Correlation ID de forma destacada
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | [%(correlation_id)s] | %(name)s | %(message)s"
    )
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware FastAPI de alta performance que gera ou propaga um Correlation ID único
    por transação HTTP, rastreia a latência de execução (ms) e atribui cabeçalhos de tracing.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Recupera correlation ID enviado pelo cliente ou gera um novo UUID
        corr_id = request.headers.get("X-Correlation-Id") or str(uuid.uuid4())

        # 2. Configura o contexto do log assíncrono de forma coroutine-safe
        token = correlation_id_var.set(corr_id)

        start_time = time.perf_counter()
        response = None
        try:
            # 3. Executa o ciclo de vida HTTP da requisição
            response = await call_next(request)
            return response
        except Exception as e:
            logging.getLogger("request_tracing").error(
                f"Erro não tratado na requisição {request.method} {request.url.path}: {e}",
                exc_info=True,
            )
            raise e
        finally:
            # 4. Instrumentação fina e cálculo de latência exata
            process_time = time.perf_counter() - start_time
            latency_ms = process_time * 1000
            status_code = response.status_code if response else 500

            logging.getLogger("request_tracing").info(
                f"HTTP {request.method} {request.url.path} - Status: {status_code} - Latency: {latency_ms:.2f}ms"
            )

            # 5. Injeção de metadados de tracing na resposta HTTP entregue ao cliente
            if response:
                response.headers["X-Correlation-Id"] = corr_id
                response.headers["X-Process-Time-Ms"] = f"{latency_ms:.2f}"

            # 6. Desaloca o contextvar para liberar recursos e isolar execuções futuras
            correlation_id_var.reset(token)
