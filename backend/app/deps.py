from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from app.models import User
from app.security import get_current_user


def require_permission(permission: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not assigned")

        role_permissions = (current_user.role.permissions or "").split(",")
        if permission not in role_permissions and "all" not in role_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return current_user

    return dependency


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role is None or current_user.role.name not in {"super_admin", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
