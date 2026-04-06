from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

import models, schemas
from database import SessionLocal, engine

# ── Create tables ─────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Records API", version="2.0.0")

# ── Security config ───────────────────────────────────────────
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ── Helpers ───────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ── DB Dependency ─────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── AUTH LOGIC (MOVE BEFORE ROUTES) ───────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user


def require_role(allowed_roles: list):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker


# ── AUTH ROUTES ───────────────────────────────────────────────
@app.post("/auth/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if user.role in ("admin", "analyst"):
        raise HTTPException(status_code=403, detail="Cannot self-assign admin/analyst")

    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="viewer",
        is_active=True,
        created_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "id": new_user.id}


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me")
def me(current_user=Depends(get_current_user)):
    return current_user


# ── USER ROUTES ───────────────────────────────────────────────
@app.get("/users")
def get_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"]))
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    total = db.query(func.count(models.User.id)).scalar()
    return {"total": total, "data": users}


# ── RECORD ROUTES ─────────────────────────────────────────────
@app.post("/records")
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin"]))
):
    new_record = models.Record(**record.dict(), user_id=user.id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@app.get("/records")
def get_records(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin", "analyst"]))
):
    query = db.query(models.Record)

    if search:
        query = query.filter(models.Record.notes.ilike(f"%{search}%"))  # ✅ FIXED

    return query.all()


# ── DASHBOARD ────────────────────────────────────────────────
@app.get("/dashboard/summary")
def summary(
    db: Session = Depends(get_db),
    user=Depends(require_role(["admin", "analyst", "viewer"]))
):
    income = db.query(func.sum(models.Record.amount)).filter(models.Record.type == "income").scalar() or 0
    expense = db.query(func.sum(models.Record.amount)).filter(models.Record.type == "expense").scalar() or 0

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense
    }