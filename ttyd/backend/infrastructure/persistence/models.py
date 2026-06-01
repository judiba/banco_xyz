from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserRecord:
    id: str
    username: str
    password_hash: str
    display_name: str
    email: str | None = None
    roles: list[str] = field(default_factory=lambda: ["ttyd:user"])
    tenant_id: str | None = None
    ad_oid: str | None = None
    auth_provider: str = "local"
    is_active: bool = True
    must_change_password: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "passwordHash": self.password_hash,
            "displayName": self.display_name,
            "email": self.email,
            "roles": self.roles,
            "tenantId": self.tenant_id,
            "adOid": self.ad_oid,
            "authProvider": self.auth_provider,
            "isActive": self.is_active,
            "mustChangePassword": self.must_change_password,
        }


@dataclass
class FolderRecord:
    id: str
    user_id: str
    name: str
    slug: str
    created_at: int
    updated_at: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "name": self.name,
            "slug": self.slug,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


@dataclass
class ConversationRecord:
    id: str
    user_id: str
    title: str
    description: str | None
    last_updated_at: int
    folder_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "description": self.description,
            "lastUpdatedAt": self.last_updated_at,
            "folderId": self.folder_id,
        }


@dataclass
class MessageRecord:
    id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    created_at: int
    status: str = "completed"
    feedback: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "conversationId": self.conversation_id,
            "userId": self.user_id,
            "role": self.role,
            "content": self.content,
            "createdAt": self.created_at,
            "status": self.status,
            "feedback": self.feedback,
        }
