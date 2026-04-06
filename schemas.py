from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime, date


# ══════════════════════════════════════════════════════════════════════════════
# USER SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = "viewer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|analyst|viewer)$")


# ══════════════════════════════════════════════════════════════════════════════
# RECORD SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=2)
    date: date   # ✅ changed from string → proper date type
    notes: Optional[str] = None


class RecordUpdate(BaseModel):
    """Partial update schema (PATCH)."""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None   # ✅ matches JWT payload
    role: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# PAGINATION (GENERIC - ADVANCED)
# ══════════════════════════════════════════════════════════════════════════════

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    data: List[T]