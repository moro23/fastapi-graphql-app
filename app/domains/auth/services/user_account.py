from typing import List, Any
from config.settings import settings
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from domains.auth.services.password_reset import password_reset_service
from db.base_class import UUID
from domains.auth.respository.user_account import users_form_actions as users_form_repo
from domains.auth.schemas.user_account import UserSchema, UserCreate, UserUpdate
from services.email_service import Email
from domains.auth.apis.login import send_reset_email




class UserService:

    def list_users_forms(self, *, db: Session, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        users_form = users_form_repo.get_all(db=db, skip=skip, limit=limit)
        return users_form




    async def create_user(self, *, db: Session, users_form: UserCreate) -> UserSchema:
            # Assuming users_form_repo is properly defined and imported
            check_if_user_email_exists = users_form_repo.get_by_email(db, users_form.email)
            if check_if_user_email_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email {users_form.email} already exists"
                )
        
            user_db = await users_form_repo.create(db=db, obj_in=users_form)

            token = password_reset_service.generate_reset_token()
            user_db.reset_password_token  = token
            db.commit()

            # Send email with the reset link
            reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"

            email_data = await send_reset_email(users_form.username, users_form.email, reset_link)

            await Email.sendMailService(email_data, template_name='password_reset.html')
            return user_db




    def update_users_forms(self, *, db: Session, id: UUID, users_form: UserUpdate) -> UserSchema:
        users_form_ = users_form_repo.get(db=db, id=id)
        if not users_form_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found")
        users_form_ = users_form_repo.update(db=db, db_obj=users_form_, obj_in=users_form)
        return users_form_

    def get_user_by_id(self, *, db: Session, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(db=db, id=id)
        if not users_form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found")
        return users_form

    def delete_users_forms(self, *, db: Session, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(db=db, id=id)
        if not users_form:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found")
        users_form = users_form_repo.remove(db=db, id=id)
        return users_form

    def get_users_forms_by_id(self, *, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(id)
        if not users_form:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="users_form not found"
            )
        return users_form

    def get_users_forms_by_keywords(self, *, db: Session, tag: str) -> List[UserSchema]:
        pass

    def search_users_forms(self, *, db: Session, search: str, value: str) -> List[UserSchema]:
        pass

    def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return users_form_repo.get_by_kwargs(self, db, kwargs)


users_forms_service = UserService()