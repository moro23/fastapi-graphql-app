from domains.auth.models.roles import Role
from domains.auth.models.users import User
from utils.security import pwd_context
from sqlalchemy.orm import Session 
from uuid import uuid4


SUPER_ADMIN_NAME: str = "Super Administrator"
SUPER_ADMIN_PHONE_NUMBER: str = "9876543210"
SUPER_ADMIN_EMAIL: str = "superadmin@admin.com"
SUPER_ADMIN_PASSWORD: str = "openforme"
SUPER_ADMIN_ROLE: str = "Super Admin"
SUPER_ADMIN_STATUS: bool = True


def init_db(db: Session):
    ## check if a super admin does not exitst and create super admin

    # # Check if the super_admin role already exists
    super_admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
    if super_admin_role:
        return  # super_admin role already exists, no need to initialize

    # Create the super_admin role
    super_admin_role = Role(id=uuid4(), name="Super Admin")
    reviewer_role = Role(id=uuid4(), name="Reviewer")
    editor_role = Role(id=uuid4(), name="Editor")
    db.add(super_admin_role)
    db.add(reviewer_role)
    db.add(editor_role)
    db.commit()

    # # Define the required permissions
    # permission_names = ["read", "create", "write", "update", "delete", "approve"]

    # # Create and assign the permissions to the super_admin role
    # for perm_name in permission_names:
    #     permission = db.query(Permission).filter(Permission.name == perm_name).first()
    #     if not permission:
    #         permission = Permission(id=uuid4(), name=perm_name)
    #         db.add(permission)
    #         db.commit()
        
    #     # Add permission to the role
    #     super_admin_role.permissions.append(permission)

    # db.commit()








def create_super_admin(db: Session):

    # Create 1st Superuser
    admin = db.query(User).filter(User.email == "superadmin@admin.com").first()       

    role = db.query(Role).filter(Role.name == "Super Admin").first()

    if admin:
        return        
    else:
        admin_in = User(
        username=SUPER_ADMIN_NAME,
        email=SUPER_ADMIN_EMAIL,
        password=pwd_context.hash(SUPER_ADMIN_PASSWORD),
        reset_password_token=None,
        #staff_id=uuid4(),
        role_id=role.id
        )
        db.add(admin_in)
        db.commit()
        db.refresh(admin_in)
