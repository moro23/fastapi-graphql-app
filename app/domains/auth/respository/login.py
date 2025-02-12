from crud.base import CRUDBase
from domains.auth.models.users import User
from domains.auth.schemas.user_account import (
    UserCreate, UserUpdate
)


class CRUDLoggedUser(CRUDBase[User, UserCreate, UserUpdate]):
    pass
logged_in_users_actions = CRUDLoggedUser(User)