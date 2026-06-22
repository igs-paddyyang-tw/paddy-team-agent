"""認證 + RBAC — API Key 認證 + admin/member/viewer 三級權限。"""
from __future__ import annotations

import hashlib
import os
from enum import IntEnum
from functools import wraps

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

# ── 角色定義 ──

class Role(IntEnum):
    VIEWER = 1    # 只能查看
    MEMBER = 2    # 查看 + 派工
    ADMIN = 3     # 全部權限


# ── API Key 認證 ──

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# 從環境變數載入 API Keys（格式：key:role,key:role）
# 例：PLATFORM_API_KEYS=abc123:admin,def456:member
def _load_keys() -> dict[str, Role]:
    raw = os.environ.get("PLATFORM_API_KEYS", "")
    if not raw:
        # 開發模式：無 key 設定時允許全部（admin）
        return {}
    keys = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" in entry:
            key, role_str = entry.split(":", 1)
            role_map = {"admin": Role.ADMIN, "member": Role.MEMBER, "viewer": Role.VIEWER}
            keys[key.strip()] = role_map.get(role_str.strip(), Role.VIEWER)
    return keys

_API_KEYS = _load_keys()


def get_role(request: Request) -> Role:
    """從 request header 取得角色。無 key 設定時預設 ADMIN（開發模式）。"""
    if not _API_KEYS:
        return Role.ADMIN  # 開發模式
    key = request.headers.get("X-API-Key", "")
    if key in _API_KEYS:
        return _API_KEYS[key]
    raise HTTPException(401, "Invalid or missing API key")


def require_role(min_role: Role):
    """FastAPI dependency — 要求最低角色。"""
    def checker(request: Request):
        role = get_role(request)
        if role < min_role:
            raise HTTPException(403, f"Requires {min_role.name} role, you have {role.name}")
        return role
    return checker


# ── Telegram 使用者權限 ──

def get_tg_role(user_id: int, access_config: dict) -> Role:
    """從 team.yaml access 設定判斷 TG 使用者角色。"""
    admin_ids = access_config.get("admin_users", [])
    allowed_ids = access_config.get("allowed_users", [])

    if user_id in admin_ids:
        return Role.ADMIN
    if user_id in allowed_ids:
        return Role.MEMBER
    if access_config.get("mode") == "open":
        return Role.VIEWER
    return Role.VIEWER


# ── 端點權限表 ──

ENDPOINT_PERMISSIONS = {
    # Admin endpoints
    "/api/admin/": Role.MEMBER,
    "/api/admin/queue/batch": Role.ADMIN,
    "/api/admin/costs/budget": Role.ADMIN,
    # Agent control
    "DELETE /api/agents/": Role.ADMIN,
    "POST /api/agents": Role.ADMIN,
    # Issue operations
    "POST /api/issues": Role.MEMBER,
    "PATCH /api/issues/": Role.MEMBER,
    # Read-only
    "GET /api/": Role.VIEWER,
}
