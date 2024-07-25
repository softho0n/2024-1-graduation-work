import json
from datetime import datetime, timedelta, timezone
from typing import List, Union

import requests
from const import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from crud import (  # add_chat,; db_add_friend,; db_get_friend_info,; db_update_user,; get_chat,
    db_charge_money,
    db_create_new_user,
    db_get_user,
    db_get_user_by_nickname,
    db_get_user_by_username,
    db_update_user,
)
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import ChargeRequest, LoginRequest, SignUpRequest, Token, TokenRequest
from passlib.context import CryptContext
from pymongo import MongoClient
from typing_extensions import Annotated
from utils import (
    create_access_token,
    get_password_hash,
    validate_token,
    verify_password,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

# client = MongoClient(host="mongo-svc", port=27017, username="adminuser", password="password123")
client = MongoClient()
db = client.test_database
user_collection = db.charge

origins = [
	"*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/payments/charge")
def charge_money(request: ChargeRequest):
    username = validate_token(request.access_token)
    
    if username:
        if db_get_user(user_collection, username) is None:
            db_create_new_user(user_collection, username, int(request.money_amount))
        else:  
            src_document = {"username": username}
            update_query = {"$inc": {"money": int(request.money_amount)}}
            db_charge_money(user_collection, src_document, update_query)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Access Token."
        ) 
        
@app.post("/payments/get_money")
def get_money(request: TokenRequest):
    username = validate_token(request.access_token)
    
    if username:
        current_user = db_get_user(user_collection, username)
        return {"username": username, "money": current_user["money"]}
    else:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Access Token."
        ) 