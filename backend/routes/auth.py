from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from database import get_db
from models.user import User, UserRole, SubscriptionTier
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    decode_access_token,
    get_user_by_id,
    update_last_login,
)
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

DEMO_USER_EMAIL = "demo@csrd-agent.app"
DEMO_USER_PASSWORD = "demo-internal-only"


def get_or_create_demo_user(db: Session) -> User:
    from services.auth_service import get_user_by_email
    user = get_user_by_email(db, DEMO_USER_EMAIL)
    if not user:
        user = create_user(
            db,
            email=DEMO_USER_EMAIL,
            password=DEMO_USER_PASSWORD,
            full_name="Demo User",
        )
    return user


# ─── Schemas ────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    subscription_tier: str
    is_active: bool


# ─── Dependency ─────────────────────────────────────────────────────────────
def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        return get_or_create_demo_user(db)
    payload = decode_access_token(token)
    if not payload:
        return get_or_create_demo_user(db)
    user_id = payload.get("sub")
    if not user_id:
        return get_or_create_demo_user(db)
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        return get_or_create_demo_user(db)
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ─── Endpoints ──────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    from services.auth_service import get_user_by_email
    from models.company import Company

    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create company if provided
    company_id = None
    if payload.company_name:
        company = Company(name=payload.company_name)
        db.add(company)
        db.flush()
        company_id = str(company.id)

    user = create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        company_id=company_id,
    )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _user_to_dict(user),
    }


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    update_last_login(db, user)
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _user_to_dict(user),
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return _user_to_dict(current_user)


@router.put("/me")
def update_profile(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_fields = {"full_name"}
    for field, value in payload.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return _user_to_dict(current_user)


def _user_to_dict(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "subscription_tier": user.subscription_tier.value,
        "company_id": str(user.company_id) if user.company_id else None,
        "is_active": user.is_active,
    }
