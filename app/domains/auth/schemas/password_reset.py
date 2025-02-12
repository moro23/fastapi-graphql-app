from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import UUID4, BaseModel, Field,validator
import uuid

## pydantic model for reset password request
class ResetPasswordRequest(BaseModel):
    email: str

## Pydantic model for resetting the password
class ResetPasswordForm(BaseModel):
    token: str
    new_password: str