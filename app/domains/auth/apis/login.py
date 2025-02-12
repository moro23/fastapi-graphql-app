from domains.auth.services.password_reset import password_reset_service
from fastapi import FastAPI, APIRouter,Depends,status,Response,Request
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.services import login as service_login
from fastapi.security import OAuth2PasswordRequestForm
from domains.auth.services import login as loginService
from services.email_service import EmailSchema,Email 
from slowapi.middleware import SlowAPIMiddleware 
from fastapi.responses import PlainTextResponse
from domains.auth.schemas import auth as schema
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import HTTPException
from slowapi.util import get_remote_address
from domains.auth.models.users import User
from fastapi.responses import JSONResponse
from config.settings import settings
from sqlalchemy.orm import Session
from datetime import datetime
from db.session import get_db
from slowapi import Limiter
import os



app = FastAPI()

# Authentication module for admins and users
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)





# Initialize the Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, limiter._rate_limit_exceeded_handler)

# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

# Custom exception handler for rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return Response(
        content="Rate limit exceeded, resulting in the account been locked.\nPlease try again in 10minutes later.",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )







@auth_router.post("/token")
async def login_for_both_access_and_refresh_tokens(request: Request, response:Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user_sign_in = await loginService.log_user_in(request=request, response=response, db=db, form_data=form_data)
        return user_sign_in

    except HTTPException as ex:
        if ex.status_code == status.HTTP_401_UNAUTHORIZED:
            print("ex error: ", ex)
            raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))
        else:
            raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))

    except RateLimitExceeded as ex:
        user = db.query(User).filter(User.email == form_data.username).first()
        if user:
            user.lock_account(lock_time_minutes=10)
            db.commit()
            
           
        raise HTTPException(status_code=ex.status_code, detail="Account locked due to too many attempts, please try again in 10 minutes.")

    except Exception as ex:
        print("Unexpected error in login: ", ex)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")









@auth_router.post("/refresh")
def get_new_access_token(response:Response, refresh_token: schema.RefreshToken, db: Session = Depends(get_db)):

    token_dict = service_login.get_new_access_token(response, refresh_token, db)
    return token_dict




@auth_router.post("/get-me")
def get_current_user_by_access_token(token:schema.AccessToken, request: Request,db: Session = Depends(get_db)):
    get_current_user = service_login.get_current_user_by_access_token(token, request, db)
    return get_current_user




async def send_reset_email(username: str, email: str, reset_link: str) -> EmailSchema:
    ## prepare the email data
    email_data = EmailSchema(
        subject= "Password Reset Request",
        email=  [email],
        body= {
            "system_logo": settings.SYSTEM_LOGO,
            "username": username,  # replace with actual username
            "name": email, 
            "reset_link": reset_link,
            "app_name": settings.PROJECT_NAME
        }
    )

    return email_data







@auth_router.get("/intruder/logs", response_class=PlainTextResponse)
async def show_intruder_logs(date: str = None):
    """
    Retrieve and display intruder logs for a specified date.
    If no date is provided, retrieve logs for the current date.
    """

    today = datetime.now().strftime("%Y-%m-%d")
    if date is None:
        date = today
        
    
    log_filename = f"intruder_log_{date}.txt"
    log_file_path = os.path.join("security/logs/", log_filename)
    print("is directory exist: ", os.path.exists(log_file_path))
    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    
    with open(log_file_path, "r") as log_file:
        log_data = log_file.read()
    
    return PlainTextResponse(log_data)