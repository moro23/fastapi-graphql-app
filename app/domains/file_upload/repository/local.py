from app.domains.file_upload.schemas.gcs import (
    FileUploadCreate, FileUploadUpdate
)
from crud.base import CRUDBase
from domains.file_upload.models.gcs import FileUpload


class CRUDFileUpload(CRUDBase[FileUpload, FileUploadCreate, FileUploadUpdate]):
    pass


fileUploads_actions = CRUDFileUpload(FileUpload)
