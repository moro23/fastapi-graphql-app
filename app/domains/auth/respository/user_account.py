from crud.base import CRUDBase
from domains.auth.models.users import User
from domains.auth.schemas.user_account import (
    UserCreate, UserUpdate
)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    pass
users_form_actions = CRUDUser(User)