from domains.auth.respository.user_account import users_form_actions as users_form_repo
from domains.auth.services.user_account import users_forms_service as actions
from domains.auth.services.password_reset import password_reset_service
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.schemas import user_account as schemas
from domains.auth.apis.login import send_reset_email
from starlette.status import HTTP_404_NOT_FOUND
from utils.rbac import check_user_role
from fastapi import APIRouter, Depends,status
from domains.auth.models.users import User
from fastapi.responses import JSONResponse
from services.email_service import Email
from config.settings import settings
from sqlalchemy.orm import Session
from fastapi import HTTPException
from db.session import get_db
from typing import Any, List, Annotated
from pydantic import UUID4




users_router = APIRouter(
       prefix="/users",
    tags=["Users Account"],
    responses={404: {"description": "Not found"}},
)





@users_router.get(
    "/all",
    response_model=List[schemas.UserSchema],
    dependencies=[Depends(check_user_role(['Super Admin']))]
)
def list_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))]
) -> Any:
    users_router = actions.list_users_forms(db=db, skip=skip, limit=limit)
    return users_router


@users_router.post(
    "/",
    response_model=schemas.UserSchema, dependencies=[Depends(check_user_role(['Super Admin']))],
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    users_forms_in: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    # Await the async create_user function
    user = await actions.create_user(db=db, users_form=users_forms_in)
    return user


@users_router.put(
    "/{id}",
    response_model=schemas.UserSchema, 
    dependencies=[Depends(check_user_role(['Super Admin']))]
)
def update_users(
        *, db: Session = Depends(get_db),
        id: UUID4,
        users_forms_in: schemas.UserUpdate
) -> Any:
    users_router = actions.get_user_by_id(db=db, id=id)
    if not users_router:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="users_forms_router not found"
        )
    users_router = actions.update_users_forms(db=db, id=users_router.id, users_form=users_forms_in)
    return users_router


@users_router.get(
    "/{id}",
    response_model=schemas.UserSchema, 
    dependencies=[Depends(check_user_role(['Super Admin']))]
)
def get_users(
        *, db: Session = Depends(get_db),
        id: UUID4
) -> Any:
    users_router = actions.get_user_by_id(db=db, id=id)
    if not users_router:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="users_forms_router not found"
        )
    return users_router









@users_router.delete(
    "/{id}",
    response_model=schemas.UserSchema, 
    dependencies=[Depends(check_user_role(['Super Admin']))]
)
def delete_users(
        *, db: Session = Depends(get_db),
        id: UUID4
) -> Any:
    users_forms_router = actions.get_user_by_id(db=db, id=id)
    if not users_forms_router:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="users_forms_router not found"
        )
    users_router = actions.delete_users_forms(db=db, id=id)
    return users_router








@users_router.post("/forgot_password/")
async def request_password_reset(reset_password_request: ResetPasswordRequest, db: Session = Depends(get_db)):
    ## confirm user email 
    user = db.query(User).filter(User.email == reset_password_request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token
    token = password_reset_service.generate_reset_token()
    user.reset_password_token = token
    db.commit()

    # Send email with the reset link
    reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"
    
    # In production, send email with aiosmtplib or any other email library
    email_data = await send_reset_email(user.username, user.email, reset_link)

    # print(f"email_data: {email_data}")

    await Email.sendMailService(email_data, template_name='forgot-password.html')
    
    return JSONResponse(content={"message": "Password reset link has been sent to your email."}, status_code=200)










@users_router.put("/reset-password-token/{token}", response_model=schemas.UserSchema)
async def update_user_with_reset_password_token(*, db: Session = Depends(get_db), token: str, obj_in: schemas.UpdatePassword):
    update_user = users_form_repo.get_by_reset_password_token(db=db, token=token)
    if not update_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Token")

    data = users_form_repo.update_user_after_reset_password(db=db, db_obj=update_user, obj_in=obj_in)
    db.refresh(data)
    return data