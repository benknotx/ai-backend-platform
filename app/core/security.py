from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import  Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import app.models as DBmodels
from app.database.session import get_db
from app.models import User




password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password:str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail= "Couldn't Validate Credentials",)
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception  
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user(user_name: str, password: str, db):
    existing_user = db.query(DBmodels.User).filter(DBmodels.User.username == user_name).first()
    if existing_user:
        raise HTTPException(status_code= 403, detail=" Username alreay exists.")
    hashed_password = hash_password(password)
    new_user = DBmodels.User(username=user_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

def login_auth(username ,password, db):
    user = db.query(DBmodels.User).filter(DBmodels.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}) 
    return {"access_token": access_token, "token_type": "bearer"}