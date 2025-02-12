from typing import List, Optional, Union,Annotated
from pydantic import BaseModel, Field, field_validator
# from domains.appraisal.schemas.permissions import PermissionCreate, Permission

from uuid import UUID
class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=50, example="admin")
    

    @field_validator('name')
    def name_must_not_be_empty(cls, value):
        if not value or value.isspace() or (value.lower() == 'string'):
            raise ValueError("Role name must not be empty or only whitespace or string")
        return value

class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, example="admin")
    # permissions: List[PermissionCreate] = []

    # @field_validator('permissions')
    # def permissions_must_be_valid(cls, value):
    #     if not isinstance(value, PermissionCreate):
    #         raise ValueError("Invalid permission data")
    #     return value

class RoleUpdate(RoleBase):
    pass
    
class RoleRead(RoleBase):
    id: UUID
    name: str 
    #permissions: List[Permission] = []

    class Config:
        orm_mode = True
