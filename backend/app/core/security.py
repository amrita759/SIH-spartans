"""
backend/app/core/security.py
Security utilities, role definitions, and access control for SIH26184.
"""

from enum import Enum
from typing import Optional
from fastapi import Header, HTTPException, status

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    LEA_OFFICER = "LEA_OFFICER"

def get_current_user_role(
    x_user_role: Optional[str] = Header(default="LEA_OFFICER", description="Operational LEA user role"),
    x_api_key: Optional[str] = Header(default=None, description="Optional API key for authorization")
) -> str:
    """
    Validates user role for law enforcement dashboard interactions.
    Defaults to LEA_OFFICER for prototype access.
    """
    valid_roles = {role.value for role in UserRole}
    role_upper = (x_user_role or "LEA_OFFICER").upper()
    if role_upper not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid user role '{x_user_role}'. Allowed roles: {list(valid_roles)}"
        )
    return role_upper
