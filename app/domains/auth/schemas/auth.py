from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import UUID4, BaseModel, Field,validator
import uuid





class TokenPayload(BaseModel):
    email: Optional[str]
    contact: Optional[str]
    exp: Optional[int]


class TokenData(BaseModel):
    username: Optional[str] = None
    expires: datetime


class RefreshToken(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str


class ShowAdmin(BaseModel):
    id: int
    email: str


class LoginModel(BaseModel):
    email: Optional[str]
    password: Optional[str]


class Settings(BaseModel):
    authjwt_secret_key: str = (
        "f7ba61299699cb4ca16a09a5ee5fe6aa3db551acf4a5959c1063f7320c13a77e"
    )



class RefreshTokenResponse(BaseModel):
    new_access_token: Optional[str]
    token_type: Optional[str]
    refresh_token: Optional[str]
    status: Optional[str]

