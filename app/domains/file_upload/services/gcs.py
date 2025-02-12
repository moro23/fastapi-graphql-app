import random
import string
from datetime import datetime
from typing import Optional, Annotated

from domains.auth.models.users import User
from domains.auth.respository.user_account import users_form_actions as users_form_repo
from domains.file_upload.models.gcs import FileUpload
from domains.file_upload.services.gcstorage import GCStorage
from fastapi import File, UploadFile, status, Form, Depends
from fastapi.exceptions import HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import check_user_role


class GCSFileUploadService:
    def get_uploaded_file_by_id(
            self, *, db: Session,
            current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))],
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

        if deleted_by: deleted_by_data = {
            "username": deleted_by.username,
            "email": deleted_by.email
        }

        db_data = {
            "id": get_uploaded_file.id,
            "url": get_uploaded_file.url,
            "file_type": get_uploaded_file.file_type,
            "description": get_uploaded_file.description,
            "name_of_project": get_uploaded_file.name_of_project,
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
            current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))],
            type: Annotated[str, Form()],
            description: Annotated[str, Form()], name_of_project: Annotated[str, Form()],
            file: Optional[UploadFile] = File(None),
    ):
        size = 10
        chars = string.ascii_lowercase + string.digits
        create_ramdom = ''.join(random.choice(chars) for _ in range(size))
        filename = create_ramdom + "-" + str(current_user.id) + "-" + file.filename
        file_url_path = GCStorage().upload_file_to_gcp(url=file, type=type, filename=filename)
        if not file_url_path: raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while uploading file"
        )
        upload_file = FileUpload(
            uploaded_by=current_user.id,
            url=file_url_path,
            type_of_upload="gcs",
            file_type=type,
            description=description,
            name_of_project=name_of_project,
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
            "name_of_project": upload_file.name_of_project,
            "type_of_upload": upload_file.type_of_upload,
            "uploaded_by": {
                "username": user_db.username,
                "email": user_db.email
            },
            "is_deleted": upload_file.is_deleted,
            "deleted_at": upload_file.deleted_at,
            "deleted_reason": upload_file.deleted_reason,
            "deleted_by": upload_file.deleted_by,
            "created_at": upload_file.created_date,
            "updated_at": upload_file.updated_date,
        }

        return db_data

    def remove_upload_file(
            self, *, db: Session,
            current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))],
            file_id: UUID4,
            deleted_reason: str,
    ):

        get_file = (
            db.query(FileUpload)
            .filter(FileUpload.id == file_id)
            .first()
        )
        delete_file = GCStorage().delete_file_to_gcp(type=get_file.file_type, filename=get_file.filename)
        if not delete_file: raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while deleting file"
        )

        db.query(FileUpload).filter(FileUpload.id == file_id).update({
            FileUpload.is_deleted: True,
            FileUpload.deleted_reason: deleted_reason,
            FileUpload.deleted_by: current_user,
            FileUpload.deleted_at: datetime.utcnow()
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


gcs_file_upload_service = GCSFileUploadService()
