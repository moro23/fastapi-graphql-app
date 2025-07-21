import strawberry 
from typing import Any, List, Optional
from strawberry.types import Info
from domains.auth.models.users import User as UserModel 
from domains.auth.models.roles import Role as RoleModel 
from sqlalchemy.orm import Session 

## lets create helper functions to get the current user and role from the context 
def get_current_user_from_context(info: Info) -> Optional[UserModel]:
    return info.context.get("current_user")

class IsAuthenticated(strawberry.permission.BasePermission):
    message = "User is not authenticated."
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        current_user = get_current_user_from_context(info)
        return current_user is not None
    
class _HasRole(strawberry.permission.BasePermission):
    message = "User does not have the required role."

    required_roles: List[str] = []
    
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        current_user = get_current_user_from_context(info)
        if not current_user:
            return False
        
        db: Session = info.context["db"]
        user_role = db.query(RoleModel).filter(RoleModel.id == current_user.role_id).first()

        if not user_role or user_role.name not in self.required_roles:
            return False
        return True 
    
def HasRole(roles: List[str]) -> type:
    """
    A factory that creates a new permission class with the required roles
    """

    return type(
        "HasRolePermission", 
        (_HasRole,),
        {"required_roles": roles}
    )