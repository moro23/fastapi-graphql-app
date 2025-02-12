from typing import Any
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base_class import APIBase
from domains.auth.models.users import User

# Define the association table
class Role(APIBase):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, index=True)
    
  
