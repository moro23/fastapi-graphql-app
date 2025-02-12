from typing import Optional

from pydantic import BaseModel, field_validator
from pydantic import UUID4


class FileUploadBase(BaseModel):
    url: Optional[str]
    filename: Optional[str]
    type: Optional[str]
    description: Optional[str]
    name_of_project: Optional[str]
    user_id: UUID4

    @field_validator('type', mode='before')
    def check_non_empty_and_not_string(cls, v, info):
        if isinstance(v, str) and (v.strip() == '' or v.strip().lower() == 'string'):
            raise ValueError(f'\n{info.field_name} should not be empty "string"')
        # make minimum value 1
        return v


class FileUploadCreate(FileUploadBase):
    url: str
    name_of_project: str


class FileUploadUpdate(FileUploadBase):
    pass


class FileUploadInDBBase(FileUploadBase):
    id: UUID4

    class Config:
        orm_mode = True


class FileUploadSchema(FileUploadInDBBase):
    pass
