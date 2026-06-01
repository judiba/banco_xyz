from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.messages import BaseMessage
from backend.app_config.bedrock import get_aws_session
from backend.app_config.settings import settings
import logging

logger = logging.getLogger(__name__)


class GerenciadorMemoria:
    def __init__(
        self,
        db_table_name: str,
        ttl: int = 2592000,
        max_messages: int = 20,
    ):
        self._table = db_table_name
        self._ttl = ttl
        self._max_messages = max_messages

        # Modo Offline: Não inicializa AWS
        if settings.DEV_OFFLINE:
            logger.info(
                f"MODO OFFLINE ATIVO: GerenciadorMemoria simulado para tabela {db_table_name}"
            )
            self.session = None
            self.dynamodb = None
            self.table = None
            return

        try:
            self.session = get_aws_session()
            self.dynamodb = self.session.resource("dynamodb")
            self.table = self.dynamodb.Table(db_table_name)
        except Exception as e:
            logger.error(f"Erro ao inicializar AWS DynamoDB: {e}")
            if not settings.DEV_OFFLINE:
                raise e

    def _history(self, session_id: str):
        if settings.DEV_OFFLINE:
            # Mock simples para histórico
            class MockHistory:
                def __init__(self):
                    self.messages = []

                def add_user_message(self, m):
                    pass

                def add_ai_message(self, m):
                    pass

            return MockHistory()

        return DynamoDBChatMessageHistory(
            table_name=self._table,
            session_id=session_id,
            ttl=self._ttl,
            ttl_key_name="expireAt",
            primary_key_name="SessionId",
            boto3_session=self.session,
        )

    # ✅ carregar histórico bruto
    def carregar(self, session_id: str) -> list[BaseMessage]:
        if settings.DEV_OFFLINE:
            return []
        return self._history(session_id).messages

    # ✅ salvar nova interação
    def salvar(self, session_id: str, user_message: str, ai_message: str):
        if settings.DEV_OFFLINE:
            return
        history = self._history(session_id)
        history.add_user_message(user_message)
        history.add_ai_message(ai_message)

    # ✅ pegar resumo persistido
    def carregar_resumo(self, session_id: str) -> str:
        if settings.DEV_OFFLINE:
            return ""
        try:
            response = self.table.get_item(Key={"SessionId": session_id})
            item = response.get("Item", {})
            return item.get("summary", "")
        except Exception as e:
            logger.warning(f"Erro ao carregar resumo: {e}")
            return ""

    # ✅ salvar resumo persistido
    def salvar_resumo(self, session_id: str, summary: str):
        if settings.DEV_OFFLINE:
            return
        try:
            self.table.update_item(
                Key={"SessionId": session_id},
                UpdateExpression="SET summary = :s",
                ExpressionAttributeValues={":s": summary},
            )
        except Exception as e:
            logger.warning(f"Erro ao salvar resumo: {e}")

    def deletar_sessao(self, session_id: str):
        if settings.DEV_OFFLINE:
            return
        try:
            self.table.delete_item(Key={"SessionId": session_id})
        except Exception as e:
            logger.warning(f"Erro ao deletar sessão: {e}")

    # ✅ construir contexto inteligente
    def construir_contexto(self, session_id: str):
        if settings.DEV_OFFLINE:
            return "", [], []

        history = self.carregar(session_id)
        summary = self.carregar_resumo(session_id)

        if len(history) <= self._max_messages:
            return summary, [], history

        old_messages = history[: -self._max_messages]
        recent_messages = history[-self._max_messages :]

        return summary, old_messages, recent_messages
