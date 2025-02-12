from fastapi import HTTPException,Depends,status,Request
from domains.auth.models.roles import Role
from fastapi.security import OAuth2PasswordBearer
from domains.auth.models.users import User
from config.settings import settings
from typing import Annotated, List
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from db.session import get_db




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")



    # function to get user or User by email
def get_user_by_email(username: str, db: Session):
    data = db.query(User).filter(User.email == username).first()
    return data

def get_user_by_id(id: str, db: Session):
    data = db.query(User).filter(User.id == id).first()
    return data

def get_all_roles(db: Session):
    data = db.query(User).all()
    return data





#function to get current user by token
def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):

    ## lets check if the cookies for access token is set
    access_token = request.cookies.get('AccessToken')

    if access_token == None:
        raise HTTPException(status_code=401, detail="Access token is invalidated")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        #print("username/email extracted is ", username)
    
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user 








#function to get active current user by token
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_active != True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="you account is not active")
    return current_user



def check_user_role(roles: list[str]):
    # print("roles", roles)
    def role_check(current_active_user: Annotated[User, Depends(get_current_user)], db: Session=Depends(get_db)):

        ## lets get the user role base on the id
        user_role = db.query(Role).filter(Role.id == current_active_user.role_id).first()
        # print("User role", user_role)
        if user_role.name not in roles: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the required permissions to perform this action")
        return user_role
    return role_check




    
