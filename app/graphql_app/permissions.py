import strawberry 
from typing import Any, List, Optional
from strawberry.types import Info
from domains.auth.models.users import User as UserModel 
from domains.auth.models.roles import Role as RoleModel 
from sqlalchemy.orm import Session 

## lets create helper functions to get the current user and role from the context 
def get_current_user(info: Info) -> Optional[UserModel]:
    return info.context.get("current_user")

class IsAuthenticated(strawberry.permission.BasePermission):
    message = "User is not authenticated."
    def has_permission(self, source: Any, info: Info) -> bool:
        current_user = get_current_user(info)
        return current_user is not None
    
class HasRole(strawberry.permission.BasePermission):
    message = "User does not have the required role."
    
    def __init__(self, role_name: str):
        self.role_name = role_name
    
    def has_permission(self, source: Any, info: Info) -> bool:
        current_user = get_current_user(info)
        if not current_user:
            return False
        db: Session = info.context["db"]
        user_role = db.query(RoleModel).filter(RoleModel.id == current_user.role_id).first()

        if not user_role or user_role.name not in self.required_roles:
            return False
        return True 