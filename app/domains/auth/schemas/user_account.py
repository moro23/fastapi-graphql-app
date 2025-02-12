from datetime import date,time, datetime
import sqlalchemy
from typing import Optional, Any, Dict
import uuid
from sqlalchemy import DateTime
from pydantic import BaseModel, field_validator, EmailStr
from pydantic import UUID4




class UserBase(BaseModel):
    username:Optional[str]
    email:EmailStr
    #password:Optional[str]
    # reset_password_token:Optional[str]
    #staff_id: UUID4
    role_id: Optional[UUID4]
    # is_active: bool = True
    # failed_login_attempts: Optional[int]
    # account_locked_until: Optional[datetime]
    # lock_count: Optional[int]


    @field_validator('email', mode='before')
    def check_non_empty_and_not_string(cls,v,info):
        if isinstance(v,str) and (v.strip() == '' or v.strip().lower() == 'string'):
            raise ValueError(f'\n{info.field_name} should not be empty "string"')
    #make minimum value 1 
        return v

      # Checking if UUID4 fields accept only UUID4 as value
    # @field_validator('staff_id', mode='before')
    # def validate_fields_with_uuid4(cls, v, info):
    #     try:
    #         uuid.UUID(str(v), version=4)
    #     except ValueError:
    #         raise ValueError(f'\n{info.field_name} must have a valid UUID4')
    #     return v

class UserCreate(UserBase):
    pass

class UpdatePassword(BaseModel):
    password: str

class UserUpdate(UserBase):
    pass

class UserInDBBase(UserBase):
    id: UUID4

    class Config:
        orm_mode= True

class UserSchema(UserInDBBase):
    pass