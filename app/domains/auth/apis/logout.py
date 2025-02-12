from fastapi import FastAPI, APIRouter,Depends,Response,Request
from domains.auth.services.logout import logout_user
from sqlalchemy.orm import Session
from db.session import get_db




app = FastAPI()

# Authentication module for admins and users
logout_auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

 

  

@logout_auth_router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    return logout_user(request=request, response=response, db=db)