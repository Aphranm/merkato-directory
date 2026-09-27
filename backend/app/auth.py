from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import AdminUser

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return passwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return passwd_context.verify(plain, hashed)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not verify_password(password, user.password): return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    if expires_delta is None: expires_delta = timedelta(days=7)
    expire = datetime.utcnow() + expires_delta
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def get_current_admin(token: str = None, db: Session = Depends(get_db)) -> AdminUser:
    if not token:
        from fastapi import Header
        auth_header = Header(None)
        if auth_header: token = auth_header.replace("Bearer ", "")
    if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

from fastapi import Header

def get_current_admin(authorization: str = Header(None), db: Session = Depends(get_db)) -> AdminUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
