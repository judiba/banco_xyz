"""Repositório DynamoDB — espelha MemoryStore."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from passlib.context import CryptContext

from backend.api.v1.utils import new_id, now_ms, slugify
from backend.app_config.settings import settings
from backend.infrastructure.persistence.memory_store import SEED_USER
from backend.infrastructure.persistence.models import (
    ConversationRecord,
    FolderRecord,
    MessageRecord,
    UserRecord,
)

logger = logging.getLogger(__name__)
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _from_dynamo(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: _from_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_from_dynamo(v) for v in obj]
    return obj


def _to_dynamo(obj: Any) -> Any:
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_dynamo(v) for v in obj]
    return obj


class DynamoDBStore:
    def __init__(self) -> None:
        prefix = settings.DYNAMODB_TABLE_PREFIX
        kwargs: dict[str, Any] = {"region_name": settings.AWS_REGION}
        if settings.DYNAMODB_ENDPOINT:
            kwargs["endpoint_url"] = settings.DYNAMODB_ENDPOINT
        self._resource = boto3.resource("dynamodb", **kwargs)
        self.users_table = self._resource.Table(f"{prefix}-users")
        self.folders_table = self._resource.Table(f"{prefix}-folders")
        self.conversations_table = self._resource.Table(f"{prefix}-conversations")
        self.messages_table = self._resource.Table(f"{prefix}-messages")
        self.tokens_table = self._resource.Table(f"{prefix}-refresh-tokens")
        self._ensure_seed_user()

    def _ensure_seed_user(self) -> None:
        try:
            resp = self.users_table.get_item(Key={"id": SEED_USER.id})
            if "Item" not in resp:
                self.users_table.put_item(
                    Item=_to_dynamo(
                        {
                            "id": SEED_USER.id,
                            "username": SEED_USER.username,
                            "passwordHash": SEED_USER.password_hash,
                            "displayName": SEED_USER.display_name,
                            "email": SEED_USER.email,
                            "roles": SEED_USER.roles,
                            "tenantId": SEED_USER.tenant_id,
                            "adOid": SEED_USER.ad_oid,
                            "authProvider": SEED_USER.auth_provider,
                            "isActive": SEED_USER.is_active,
                            "mustChangePassword": SEED_USER.must_change_password,
                        }
                    )
                )
        except ClientError as exc:
            logger.warning("Não foi possível garantir usuário seed: %s", exc)

    def verify_password(self, user: UserRecord, password: str) -> bool:
        if user.auth_provider == "microsoft":
            return False
        if not user.password_hash or user.password_hash == "__SSO_NO_PASSWORD__":
            return False
        return _pwd.verify(password, user.password_hash)

    def _user_from_item(self, item: dict) -> UserRecord:
        item = _from_dynamo(item)
        return UserRecord(
            id=item["id"],
            username=item["username"],
            password_hash=item["passwordHash"],
            display_name=item["displayName"],
            email=item.get("email"),
            roles=item.get("roles", ["ttyd:user"]),
            tenant_id=item.get("tenantId"),
            ad_oid=item.get("adOid"),
            auth_provider=item.get("authProvider", "local"),
            is_active=item.get("isActive", True),
            must_change_password=item.get("mustChangePassword", False),
        )

    def get_user_by_ad_oid(self, ad_oid: str) -> UserRecord | None:
        try:
            resp = self.users_table.query(
                IndexName="adOid-index",
                KeyConditionExpression=Key("adOid").eq(ad_oid),
            )
            items = resp.get("Items", [])
            if items:
                return self._user_from_item(items[0])
        except ClientError:
            pass
        for item in self.users_table.scan().get("Items", []):
            if item.get("adOid") == ad_oid:
                return self._user_from_item(item)
        return None

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
        self.users_table.put_item(Item=_to_dynamo(user.to_dict()))
        return user

    def get_user_by_username(self, username: str) -> UserRecord | None:
        try:
            resp = self.users_table.query(
                IndexName="username-index",
                KeyConditionExpression=Key("username").eq(username.strip()),
            )
            items = resp.get("Items", [])
            if not items:
                return None
            return self._user_from_item(items[0])
        except ClientError:
            for item in self.users_table.scan().get("Items", []):
                if item.get("username", "").lower() == username.strip().lower():
                    return self._user_from_item(item)
            return None

    def get_user(self, user_id: str) -> UserRecord | None:
        resp = self.users_table.get_item(Key={"id": user_id})
        item = resp.get("Item")
        return self._user_from_item(item) if item else None

    def _folder_from_item(self, item: dict) -> FolderRecord:
        item = _from_dynamo(item)
        return FolderRecord(
            id=item["id"],
            user_id=item["userId"],
            name=item["name"],
            slug=item["slug"],
            created_at=item["createdAt"],
            updated_at=item["updatedAt"],
        )

    def list_folders(self, user_id: str) -> list[FolderRecord]:
        resp = self.folders_table.query(
            IndexName="userId-index",
            KeyConditionExpression=Key("userId").eq(user_id),
        )
        return [self._folder_from_item(i) for i in resp.get("Items", [])]

    def get_folder(self, user_id: str, folder_id: str) -> FolderRecord | None:
        resp = self.folders_table.get_item(Key={"id": folder_id})
        item = resp.get("Item")
        if not item:
            return None
        f = self._folder_from_item(item)
        return f if f.user_id == user_id else None

    def get_folder_by_slug(self, user_id: str, slug: str) -> FolderRecord | None:
        for f in self.list_folders(user_id):
            if f.slug == slug:
                return f
        return None

    def folder_name_exists(self, user_id: str, name: str, exclude_id: str | None = None) -> bool:
        norm = name.strip().lower()
        for f in self.list_folders(user_id):
            if f.name.strip().lower() == norm and f.id != exclude_id:
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
        self.folders_table.put_item(Item=_to_dynamo(folder.to_dict()))
        return folder

    def update_folder(self, folder: FolderRecord, name: str) -> FolderRecord:
        folder.name = name.strip()
        folder.slug = slugify(name)
        folder.updated_at = now_ms()
        self.folders_table.put_item(Item=_to_dynamo(folder.to_dict()))
        return folder

    def delete_folder(self, user_id: str, folder_id: str, cascade: bool) -> int:
        deleted = 0
        if cascade:
            for c in self.list_conversations(user_id, folder_id=folder_id):
                self.delete_conversation(user_id, c.id)
                deleted += 1
        else:
            for c in self.list_conversations(user_id, folder_id=folder_id):
                c.folder_id = None
                self.conversations_table.put_item(Item=_to_dynamo(c.to_dict()))
        self.folders_table.delete_item(Key={"id": folder_id})
        return deleted

    def _conv_from_item(self, item: dict) -> ConversationRecord:
        item = _from_dynamo(item)
        return ConversationRecord(
            id=item["id"],
            user_id=item["userId"],
            title=item["title"],
            description=item.get("description"),
            last_updated_at=item["lastUpdatedAt"],
            folder_id=item.get("folderId"),
        )

    def list_conversations(
        self,
        user_id: str,
        *,
        folder_id: str | None = "__unset__",
        q: str | None = None,
    ) -> list[ConversationRecord]:
        from backend.api.v1.utils import matches_search

        resp = self.conversations_table.query(
            IndexName="userId-lastUpdatedAt-index",
            KeyConditionExpression=Key("userId").eq(user_id),
            ScanIndexForward=False,
        )
        items = [self._conv_from_item(i) for i in resp.get("Items", [])]
        if folder_id != "__unset__":
            if folder_id is None:
                items = [c for c in items if c.folder_id is None]
            else:
                items = [c for c in items if c.folder_id == folder_id]
        if q:
            items = [
                c
                for c in items
                if matches_search(c.title, q) or matches_search(c.description or "", q)
            ]
        return items

    def get_conversation(self, user_id: str, conversation_id: str) -> ConversationRecord | None:
        resp = self.conversations_table.get_item(Key={"id": conversation_id})
        item = resp.get("Item")
        if not item:
            return None
        c = self._conv_from_item(item)
        return c if c.user_id == user_id else None

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
        self.conversations_table.put_item(Item=_to_dynamo(conv.to_dict()))
        return conv

    def update_conversation(self, conv: ConversationRecord, **kwargs: Any) -> ConversationRecord:
        if kwargs.get("title") is not None:
            conv.title = kwargs["title"]
        if "folderId" in kwargs or "folder_id" in kwargs:
            conv.folder_id = kwargs.get("folderId", kwargs.get("folder_id"))
        conv.last_updated_at = now_ms()
        self.conversations_table.put_item(Item=_to_dynamo(conv.to_dict()))
        return conv

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        c = self.get_conversation(user_id, conversation_id)
        if not c:
            return False
        for m in self.list_messages(conversation_id):
            self.messages_table.delete_item(Key={"id": m.id})
        self.conversations_table.delete_item(Key={"id": conversation_id})
        return True

    def _msg_from_item(self, item: dict) -> MessageRecord:
        item = _from_dynamo(item)
        return MessageRecord(
            id=item["id"],
            conversation_id=item["conversationId"],
            user_id=item["userId"],
            role=item["role"],
            content=item["content"],
            created_at=item["createdAt"],
            status=item.get("status", "completed"),
            feedback=item.get("feedback"),
        )

    def list_messages(self, conversation_id: str) -> list[MessageRecord]:
        resp = self.messages_table.query(
            IndexName="conversationId-createdAt-index",
            KeyConditionExpression=Key("conversationId").eq(conversation_id),
            ScanIndexForward=True,
        )
        return [self._msg_from_item(i) for i in resp.get("Items", [])]

    def get_message(self, message_id: str) -> MessageRecord | None:
        resp = self.messages_table.get_item(Key={"id": message_id})
        item = resp.get("Item")
        return self._msg_from_item(item) if item else None

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
        self.messages_table.put_item(Item=_to_dynamo(msg.to_dict()))
        return msg

    def update_message_content(self, msg: MessageRecord, content: str) -> MessageRecord:
        msg.content = content
        msg.created_at = now_ms()
        msg.status = "completed"
        self.messages_table.put_item(Item=_to_dynamo(msg.to_dict()))
        return msg

    def set_message_feedback(self, msg: MessageRecord, feedback: str | None) -> MessageRecord:
        msg.feedback = feedback
        self.messages_table.put_item(Item=_to_dynamo(msg.to_dict()))
        return msg

    def count_conversations_in_folder(self, user_id: str, folder_id: str) -> int:
        return len(self.list_conversations(user_id, folder_id=folder_id))

    def save_refresh_token(self, token_id: str, user_id: str, expires_at: int) -> None:
        self.tokens_table.put_item(
            Item=_to_dynamo(
                {
                    "id": token_id,
                    "userId": user_id,
                    "expiresAt": expires_at,
                    "ttl": expires_at // 1000,
                }
            )
        )

    def get_refresh_token(self, token_id: str) -> dict[str, Any] | None:
        resp = self.tokens_table.get_item(Key={"id": token_id})
        item = resp.get("Item")
        return _from_dynamo(item) if item else None

    def delete_refresh_token(self, token_id: str) -> None:
        self.tokens_table.delete_item(Key={"id": token_id})
