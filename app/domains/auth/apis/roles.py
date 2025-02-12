from domains.auth.services.role import role_service as actions 
from domains.auth.schemas.roles import RoleUpdate,RoleRead
from starlette.status import HTTP_404_NOT_FOUND
from utils.rbac import check_user_role
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Any,List, Annotated
from pydantic import UUID4
from domains.auth.models.users import User 

## print()

from db.session import get_db



# APIRouter creates path operations for admin and users module
role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    responses={404: {"description": "Not found"}},
)




# ## create a new role 
# @role_router.post("/", response_model= RoleRead)
# async def create_new_role(*, payload: RoleCreate, db:Session=Depends(get_db)):
#     new_role = await actions.create_role(db=db, role_in=payload)
#     return new_role


## get role by the row_id 
# @role_router.get("/{id}", response_model=RoleRead)
# def get_row(*, db: Session = Depends(get_db), id: UUID4, current_user=Depends(check_if_is_super_admin)) -> Any:
#     role = actions.get_role_by_id(db=db, role_id=id)
#     if not role:
#         raise HTTPException(
#             status_code=HTTP_404_NOT_FOUND,
#             detail="role not found"
#         )
#     return role 

## endpoint to 
@role_router.get("/", response_model=List[RoleRead], dependencies=[Depends(check_user_role(['Super Admin']))])
def get_all_roles(*, db: Session = Depends(get_db), skip: int=0, limit: int=0, current_user=Annotated[User, Depends(check_user_role(["Super Admin"]))]):
    all_roles = actions.get_all_roles(db=db)
    return all_roles 

## endpoint to get current user 

# @role_router.put("/{role_id}", response_model=RoleUpdate)
# def update_role(role_id: UUID4, role_update: RoleUpdate, db: Session = Depends(get_db), current_user=Depends(check_if_is_super_admin)):
#     role_update = actions.updated_role(db, role_id, role_update)
#     return role_update
