from domains.file_upload.apis.local import local_file_upload_router
from domains.file_upload.apis.gcs import gcs_file_upload_router
from domains.auth.apis.logout import logout_auth_router
from domains.auth.apis.email_router import email_router
from domains.auth.apis.user_account import users_router
from domains.auth.apis.roles import role_router
from domains.auth.apis.login import auth_router


from fastapi import APIRouter


router = APIRouter()
#router.include_router(email_router)
router.include_router(auth_router)
router.include_router(logout_auth_router)
router.include_router(users_router)
router.include_router(gcs_file_upload_router)
# router.include_router(local_file_upload_router)
router.include_router(role_router)
# router.include_router(perm_router)


