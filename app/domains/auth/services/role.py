from typing import List, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.base_class import UUID
from domains.auth.respository.role import role_actions as role_repo 
from domains.auth.schemas.roles import RoleCreate, RoleUpdate, RoleRead

from domains.auth.models.roles import Role


class RoleService:

    async def create_role(self, *, db: Session, role_in: RoleCreate) -> RoleRead:
        check_role_name = db.query(Role).filter(Role.name == role_in.name).first()

        if check_role_name: 
            raise HTTPException (
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = 'Role name already exists'
            )
        
        new_role = await role_repo.create(db, role_in)
        return new_role

               
    def get_role_by_id(self, db: Session, role_id: UUID) -> RoleRead:
        # role = role_repo.get(db=db, id=role_id)
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="role does not exits"
            )
        return role
    
    def get_all_roles(self, db: Session, skip: int=0, limit: int=10):
        
        # return role_repo.get_all(db=db, skip=skip, limit=limit)
        return db.query(Role).offset(skip).limit(limit).all()
    
    def updated_role(self, db: Session, role_id: UUID, role_update: RoleUpdate):
        role = db.query(Role).filter(Role.id == role_id).first() 
        if not role: 
            raise HTTPException (
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = 'Role not found'
            )


        role.name = role_update.name 
        db.commit()
        db.refresh(role)
        return role 
       
        
    
    # def create_role_perm(self, *, role_perm: RoleCreate, db: Session):
    #     #Check if the role name already exists
    #     existing_role = db.query(Role).filter(Role.name == role_perm.name).first()
    #     if existing_role:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail=f"Role '{role_perm.name}' already exists."
    #             )

    #     db_role = Role(name=role_perm.name)
        # db.add(db_role)
        # db.commit()
        # db.refresh(db_role)

        # for per in role_perm.permissions:
        #     db_permission = db.query(Permission).filter(Permission.name == per.name).first()
        #     if not db_permission:
        #         db_permission = Permission(name=per.name)
        #         # db.add(db_permission)
        #         # db.commit()
        #         # db.refresh(db_permission)

        #     db_role.role_permissions.append(role_permission_table(role_id=db_role.id, permission_id=db_permission.id))
        #     # db.add(role_permission)

        # db.commit()
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    # ## function to define new roles  in the system..
    # def create_role_perm(self, *, role_perm: RoleCreate, db:Session):

    #     # Check if the role name already exists
    #     # print(role_perm.name)
    #     # print(role_perm.permissions)
    #     existing_role = db.query(Role).filter(Role.name == role_perm.name).first()
        
    #     # if existing_role:
    #     #     raise HTTPException(
    #     #         status_code=status.HTTP_400_BAD_REQUEST,
    #     #         detail=f"Role '{role_perm.name}' already exists."
    #     #     )

    #     db_role = Role(name=role_perm.name)
    #     db.add(db_role)
    #     db.commit()
    #     db.refresh(db_role)
        
    #     for per in role_perm.permissions:
    #         try:
    #             db_permission = db.query(Permission).filter(Permission.name == per.name).first()
    #             if not db_permission:
    #                 db_permission = Permission(name=per.name)
    #                 db.add(db_permission)
    #                 db.commit()
    #                 db.refresh(db_permission)
                   
    #         except Exception as e:
    #             db.rollback()
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail=f"Permission '{per.name}' already exists."
    #             )
    #         role_permission = RolePermission(role_id=db_role.id, permission_id=db_permission.id)
    #         db.add(role_permission)

        
    #     db.commit()
    #     db.refresh(db_role)
    #     return db_role


    # def update_role_perm(self, obj_in: UpdateSchemaType, db: Session, **kw):
    #     db_role = db.query(self.model).filter(self.model.id == obj_in.role_id).first()
    #     if not db_role:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
    #     db_role.name = obj_in.name
    #     db_role.permissions = []
    #     for perm in obj_in.permissions:
    #         db_permission = db.query(Permission).filter(Permission.name == perm.name).first()
    #         if not db_permission:
    #             db_permission = Permission(name=perm.name)
    #         db_role.permissions.append(db_permission)
    #     db.commit()
    #     db.refresh(db_role)
    #     return db_role
    
    
    
role_service = RoleService()