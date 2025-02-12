from typing import Optional, Annotated

from db.session import get_db
from domains.auth.models.users import User
from domains.file_upload.services.gcs import gcs_file_upload_service as actions
from fastapi import APIRouter, Depends, status
from fastapi import File, UploadFile, Form
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import get_current_user, check_user_role

gcs_file_upload_router = APIRouter(
    prefix="/gcs",
    tags=["GCS FILE UPLOAD"],
    responses={404: {"description": "Not found"}},
)


@gcs_file_upload_router.post("/", dependencies=[Depends(check_user_role(['Super Admin', 'Editor']))])
async def upload_file(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        file: UploadFile = File(...),
        type: Optional[str] = Form(),
        name_of_project: str = Form(),
        description: Optional[str] = Form(None),
):
    upload_file = actions.upload_file(
        db=db,
        type=type,
        description=description,
        name_of_project=name_of_project,
        file=file,
        current_user=current_user
    )
    return upload_file


@gcs_file_upload_router.get("/", dependencies=[Depends(check_user_role(['Super Admin', 'Editor']))])
async def get_uploaded(
        *, db: Session = Depends(get_db),
        current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))],
        file_id: UUID4,
):
    upload_file = actions.get_uploaded_file_by_id(db=db, file_id=file_id, current_user=current_user)
    return upload_file


# function to delete files
@gcs_file_upload_router.delete("/{id}", dependencies=[Depends(check_user_role(['Super Admin', 'Editor']))])
async def delete_file(
        *, db: Session = Depends(get_db),
        current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))],
        id: UUID4,
        deleted_reason: str,
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
