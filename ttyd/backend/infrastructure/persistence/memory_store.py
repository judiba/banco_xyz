"""Repositório em memória para DEV_OFFLINE e testes."""

from __future__ import annotations

from typing import Any

from passlib.context import CryptContext

from backend.api.v1.utils import new_id, now_ms, slugify
from backend.infrastructure.persistence.models import (
    ConversationRecord,
    FolderRecord,
    MessageRecord,
    UserRecord,
)

_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SEED_USER = UserRecord(
    id="550e8400-e29b-41d4-a716-446655440000",
    username="adminrecord",
    password_hash=_pwd.hash("record123"),
    display_name="Diego",
    email="diego.silva@record.com.br",
    roles=["ttyd:user"],
    tenant_id="record-br",
)

SEED_ADMIN_USER = UserRecord(
    id="660e8400-e29b-41d4-a716-446655440001",
    username="admin_ttyd",
    password_hash=_pwd.hash("record123"),
    display_name="Admin TTYD",
    email="admin@record.com.br",
    roles=["ttyd:admin"],
    tenant_id="record-br",
)


class MemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, UserRecord] = {}
        self.users_by_username: dict[str, str] = {}
        self.users_by_ad_oid: dict[str, str] = {}
        self.folders: dict[str, FolderRecord] = {}
        self.conversations: dict[str, ConversationRecord] = {}
        self.messages: dict[str, MessageRecord] = {}
        self.refresh_tokens: dict[str, dict[str, Any]] = {}
        self._seed()

    def _seed(self) -> None:
        for user in (SEED_USER, SEED_ADMIN_USER):
            self.users[user.id] = user
            self.users_by_username[user.username.strip().lower()] = user.id
        user = SEED_USER

        folder = FolderRecord(
            id="f47ac10b-58cc-4372-a567-0e02b2c3d479",
            user_id=user.id,
            name="Faturamento",
            slug="faturamento",
            created_at=1735689600000,
            updated_at=1735689600000,
        )
        self.folders[folder.id] = folder

        conv = ConversationRecord(
            id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
            user_id=user.id,
            title="Análise Audiência Domingo legal",
            description="Qual foi o desempenho de audiência no Domingo Legal?",
            last_updated_at=1741150800000,
            folder_id=None,
        )
        self.conversations[conv.id] = conv

        for mid, role, content, created in [
            (
                "a3bb189e-8bf9-3888-9912-ace4e6543001",
                "user",
                "Qual foi o desempenho de audiência no Domingo Legal?",
                1741150800000,
            ),
            (
                "a3bb189e-8bf9-3888-9912-ace4e6543002",
                "assistant",
                "Entendi. Segue um resumo da análise e próximos passos.\n\n**Destaques**\n- Share médio: 23.5 no horário das 20h",
                1741150800350,
            ),
        ]:
            self.messages[mid] = MessageRecord(
                id=mid,
                conversation_id=conv.id,
                user_id=user.id,
                role=role,
                content=content,
                created_at=created,
                feedback="like" if role == "assistant" else None,
            )

    def verify_password(self, user: UserRecord, password: str) -> bool:
        if user.auth_provider == "microsoft":
            return False
        if not user.password_hash or user.password_hash == "__SSO_NO_PASSWORD__":
            return False
        return _pwd.verify(password, user.password_hash)

    def get_user_by_ad_oid(self, ad_oid: str) -> UserRecord | None:
        uid = self.users_by_ad_oid.get(ad_oid)
        return self.users.get(uid) if uid else None

    def create_saml_user(
        self,
        *,
        ad_oid: str,
        username: str,
        email: str | None,
        display_name: str,
        role: str,
        tenant_id: str | None = None,
    ) -> UserRecord:
        user = UserRecord(
            id=new_id(),
            username=username.strip().lower(),
            password_hash="__SSO_NO_PASSWORD__",
            display_name=display_name,
            email=email,
            roles=[role],
            tenant_id=tenant_id,
            ad_oid=ad_oid,
            auth_provider="microsoft",
            is_active=True,
            must_change_password=False,
        )
        self.users[user.id] = user
        self.users_by_username[user.username] = user.id
        self.users_by_ad_oid[ad_oid] = user.id
        return user

    def get_user_by_username(self, username: str) -> UserRecord | None:
        uid = self.users_by_username.get(username.strip().lower())
        return self.users.get(uid) if uid else None

    def get_user(self, user_id: str) -> UserRecord | None:
        return self.users.get(user_id)

    def list_folders(self, user_id: str) -> list[FolderRecord]:
        return [f for f in self.folders.values() if f.user_id == user_id]

    def get_folder(self, user_id: str, folder_id: str) -> FolderRecord | None:
        f = self.folders.get(folder_id)
        return f if f and f.user_id == user_id else None

    def get_folder_by_slug(self, user_id: str, slug: str) -> FolderRecord | None:
        for f in self.folders.values():
            if f.user_id == user_id and f.slug == slug:
                return f
        return None

    def folder_name_exists(self, user_id: str, name: str, exclude_id: str | None = None) -> bool:
        norm = name.strip().lower()
        for f in self.folders.values():
            if f.user_id == user_id and f.name.strip().lower() == norm and f.id != exclude_id:
                return True
        return False

    def create_folder(self, user_id: str, name: str) -> FolderRecord:
        ts = now_ms()
        slug = slugify(name)
        base_slug = slug
        n = 1
        while self.get_folder_by_slug(user_id, slug):
            slug = f"{base_slug}-{n}"
            n += 1
        folder = FolderRecord(
            id=new_id(),
            user_id=user_id,
            name=name.strip(),
            slug=slug,
            created_at=ts,
            updated_at=ts,
        )
        self.folders[folder.id] = folder
        return folder

    def update_folder(self, folder: FolderRecord, name: str) -> FolderRecord:
        folder.name = name.strip()
        folder.slug = slugify(name)
        folder.updated_at = now_ms()
        return folder

    def delete_folder(self, user_id: str, folder_id: str, cascade: bool) -> int:
        deleted_convs = 0
        if cascade:
            for cid in list(self.conversations.keys()):
                c = self.conversations[cid]
                if c.user_id == user_id and c.folder_id == folder_id:
                    self._delete_conversation_messages(cid)
                    del self.conversations[cid]
                    deleted_convs += 1
        else:
            for c in self.conversations.values():
                if c.user_id == user_id and c.folder_id == folder_id:
                    c.folder_id = None
        del self.folders[folder_id]
        return deleted_convs

    def list_conversations(
        self,
        user_id: str,
        *,
        folder_id: str | None = "__unset__",
        q: str | None = None,
    ) -> list[ConversationRecord]:
        items = [c for c in self.conversations.values() if c.user_id == user_id]
        if folder_id != "__unset__":
            if folder_id is None:
                items = [c for c in items if c.folder_id is None]
            else:
                items = [c for c in items if c.folder_id == folder_id]
        if q:
            from backend.api.v1.utils import matches_search

            items = [
                c
                for c in items
                if matches_search(c.title, q) or matches_search(c.description or "", q)
            ]
        items.sort(key=lambda x: x.last_updated_at, reverse=True)
        return items

    def get_conversation(self, user_id: str, conversation_id: str) -> ConversationRecord | None:
        c = self.conversations.get(conversation_id)
        return c if c and c.user_id == user_id else None

    def create_conversation(
        self,
        user_id: str,
        *,
        title: str = "Novo chat",
        description: str | None = None,
        folder_id: str | None = None,
    ) -> ConversationRecord:
        ts = now_ms()
        conv = ConversationRecord(
            id=new_id(),
            user_id=user_id,
            title=title,
            description=description,
            last_updated_at=ts,
            folder_id=folder_id,
        )
        self.conversations[conv.id] = conv
        return conv

    def update_conversation(self, conv: ConversationRecord, **kwargs: Any) -> ConversationRecord:
        if "title" in kwargs and kwargs["title"] is not None:
            conv.title = kwargs["title"]
        if "folderId" in kwargs or "folder_id" in kwargs:
            conv.folder_id = kwargs.get("folderId", kwargs.get("folder_id"))
        conv.last_updated_at = now_ms()
        return conv

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        c = self.get_conversation(user_id, conversation_id)
        if not c:
            return False
        self._delete_conversation_messages(conversation_id)
        del self.conversations[conversation_id]
        return True

    def _delete_conversation_messages(self, conversation_id: str) -> None:
        for mid in list(self.messages.keys()):
            if self.messages[mid].conversation_id == conversation_id:
                del self.messages[mid]

    def list_messages(self, conversation_id: str) -> list[MessageRecord]:
        items = [m for m in self.messages.values() if m.conversation_id == conversation_id]
        items.sort(key=lambda x: x.created_at)
        return items

    def get_message(self, message_id: str) -> MessageRecord | None:
        return self.messages.get(message_id)

    def create_message(
        self,
        *,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        status: str = "completed",
    ) -> MessageRecord:
        msg = MessageRecord(
            id=new_id(),
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            created_at=now_ms(),
            status=status,
        )
        self.messages[msg.id] = msg
        return msg

    def update_message_content(self, msg: MessageRecord, content: str) -> MessageRecord:
        msg.content = content
        msg.created_at = now_ms()
        msg.status = "completed"
        return msg

    def set_message_feedback(self, msg: MessageRecord, feedback: str | None) -> MessageRecord:
        msg.feedback = feedback
        return msg

    def count_conversations_in_folder(self, user_id: str, folder_id: str) -> int:
        return sum(
            1
            for c in self.conversations.values()
            if c.user_id == user_id and c.folder_id == folder_id
        )

    def save_refresh_token(self, token_id: str, user_id: str, expires_at: int) -> None:
        self.refresh_tokens[token_id] = {"userId": user_id, "expiresAt": expires_at}

    def get_refresh_token(self, token_id: str) -> dict[str, Any] | None:
        return self.refresh_tokens.get(token_id)

    def delete_refresh_token(self, token_id: str) -> None:
        self.refresh_tokens.pop(token_id, None)


_store: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store


def reset_memory_store() -> None:
    global _store
    _store = MemoryStore()
