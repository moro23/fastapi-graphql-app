from typing import Optional

from db.session import get_db
from domains.file_upload.services.local import local_file_upload_service as actions
from fastapi import APIRouter, Depends, status
from fastapi import File, UploadFile, Form
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import check_user_role

local_file_upload_router = APIRouter(
    prefix="/local",
    tags=["LOCAL FILE UPLOAD"],
    responses={404: {"description": "Not found"}},
)


@local_file_upload_router.post("/")
async def upload_file(
        *, db: Session = Depends(get_db),
        current_user=Depends(check_user_role(['Super Admin'])),
        file: UploadFile = File(...),
        type: Optional[str] = Form(),
        description: Optional[str] = Form(None),
):
    upload_file = actions.upload_file(
        db=db,
        type=type,
        description=description,
        file=file,
        current_user=current_user
    )
    return upload_file


@local_file_upload_router.get("/")
async def get_uploaded(
        *, db: Session = Depends(get_db),
        current_user=Depends(check_user_role(['Super Admin'])),
        file_id: UUID4,
):
    upload_file = actions.get_uploaded_file_by_id(
        db=db,
        file_id=file_id,
        current_user=current_user
    )
    return upload_file


# function to delete files
@local_file_upload_router.delete("/{id}")
async def delete_file(
        *, db: Session = Depends(get_db),
        current_user=Depends(check_user_role(['Super Admin'])),
        id: UUID4, deleted_reason: str,
):
    check_file = actions.get_uploaded_file_by_id(db=db, file_id=id)
    if not check_file: raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'🚨 file does not exist - do something'
    )
    upload_file = actions.remove_upload_file(
        db=db,
        file_id=id,
        deleted_reason=deleted_reason,
        current_user=current_user.id
    )
    return upload_file
