import os
import uuid
from datetime import datetime
from typing import Optional, Annotated

from domains.auth.models.users import User
from domains.auth.respository.user_account import users_form_actions as users_form_repo
from domains.file_upload.models.gcs import FileUpload
from fastapi import File, UploadFile, status, Form, Depends
from fastapi.exceptions import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import check_user_role

# Define the directory where files will be stored
UPLOAD_DIRECTORY = "uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class LocalFileUploadService:
    def get_uploaded_file_by_id(
            self, *, db: Session,
            current_user: User = Depends(check_user_role(['super admin'])),
            file_id: UUID4,
    ):
        get_uploaded_file = (
            db.query(FileUpload)
            .filter(FileUpload.id == file_id)
            .first()
        )
        if not get_uploaded_file: raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not found"
        )

        uploaded_by = users_form_repo.get_by_id(id=get_uploaded_file.uploaded_by, db=db)
        deleted_by = users_form_repo.get_by_id(id=get_uploaded_file.deleted_by, db=db)

        deleted_by_data = {
            "username": None,
            "email": None
        }

        if deleted_by:
            deleted_by_data = {
                "username": deleted_by.username,
                "email": deleted_by.email
            }

        db_data = {
            "id": get_uploaded_file.id,
            "url": get_uploaded_file.url,
            "file_type": get_uploaded_file.file_type,
            "description": get_uploaded_file.description,
            "filename": get_uploaded_file.filename,
            "type_of_upload": get_uploaded_file.type_of_upload,
            "uploaded_by": {
                "username": uploaded_by.username,
                "email": uploaded_by.email
            },
            "is_deleted": get_uploaded_file.is_deleted,
            "deleted_by": deleted_by_data,
            "deleted_at": get_uploaded_file.deleted_at,
            "deleted_reason": get_uploaded_file.deleted_reason,
            "created_at": get_uploaded_file.created_date,
            "updated_at": get_uploaded_file.updated_date,
        }
        return db_data

    def upload_file(
            self, *, db: Session,
            current_user: User = Depends(check_user_role(['super admin'])),
            type: Annotated[str, Form()],
            description: Annotated[str, Form()], file: Optional[UploadFile] = File(None),
    ):
        if not file: raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )

        # Create a unique filename
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}-{current_user.id}-{file.filename}"
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)

        # Save the file locally
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Save file information to the database
        upload_file = FileUpload(
            uploaded_by=current_user.id,
            type_of_upload="local",
            url=file_path,
            file_type=type,
            description=description,
            filename=filename
        )
        db.add(upload_file)
        db.commit()
        db.refresh(upload_file)

        user_db = users_form_repo.get_by_id(id=current_user.id, db=db)

        db_data = {
            "id": upload_file.id,
            "url": upload_file.url,
            "file_type": upload_file.file_type,
            "description": upload_file.description,
            "filename": upload_file.filename,
            "type_of_upload": upload_file.type_of_upload,
            "uploaded_by": {
                "username": user_db.username,
                "email": user_db.email
            },
            "is_deleted": upload_file.is_deleted,
            "deleted_by": upload_file.deleted_by,
            "deleted_at": upload_file.deleted_at,
            "deleted_reason": upload_file.deleted_reason,
            "created_at": upload_file.created_date,
            "updated_at": upload_file.updated_date,
        }

        return db_data

    def remove_upload_file(
            self, *, db: Session,
            current_user: UUID4,
            file_id: UUID4,
            deleted_reason: str,
    ):

        get_file = (
            db.query(FileUpload)
            .filter(FileUpload.id == file_id)
            .first()
        )
        if not get_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not found"
            )

        # Delete file from local storage
        file_path = os.path.join(UPLOAD_DIRECTORY, get_file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on local storage"
            )

        # Update file record in the database
        db.query(FileUpload).filter(FileUpload.id == file_id).update({
            FileUpload.is_deleted: True,
            FileUpload.deleted_reason: deleted_reason,
            FileUpload.deleted_by: current_user,
            FileUpload.deleted_at: datetime.utcnow()  # Ensure to import and use correct datetime
        }, synchronize_session=False)
        db.commit()

        updated_file_upload = (
            db.query(FileUpload)
            .filter(FileUpload.id == file_id)
            .first()
        )

        uploaded_by = users_form_repo.get_by_id(id=updated_file_upload.uploaded_by, db=db)
        deleted_by = users_form_repo.get_by_id(id=updated_file_upload.deleted_by, db=db)

        db_data = {
            "id": updated_file_upload.id,
            "url": updated_file_upload.url,
            "file_type": updated_file_upload.file_type,
            "description": updated_file_upload.description,
            "filename": updated_file_upload.filename,
            "type_of_upload": updated_file_upload.type_of_upload,
            "uploaded_by": {
                "username": uploaded_by.username,
                "email": uploaded_by.email
            },
            "is_deleted": updated_file_upload.is_deleted,
            "deleted_by": {
                "username": deleted_by.username,
                "email": deleted_by.email
            },
            "deleted_at": updated_file_upload.deleted_at,
            "deleted_reason": updated_file_upload.deleted_reason,
            "created_at": updated_file_upload.created_date,
            "updated_at": updated_file_upload.updated_date,
        }
        return db_data


local_file_upload_service = LocalFileUploadService()
