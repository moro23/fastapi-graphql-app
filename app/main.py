from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI,Request,status, Depends, Response as FastAPIResponse
from fastapi.middleware.cors import CORSMiddleware
from db.init_db import init_db,create_super_admin
from apis.google_cloud_storage_api import create_service_account_json
from apis.routers import router as api_router
from domains.auth.models.users import User
from fastapi.responses import JSONResponse
from db.init_models import create_tables
from config.settings import settings
from db.session import SessionLocal, get_db
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import requests
import uvicorn
import json
import os

from strawberry.fastapi import GraphQLRouter
from graphql_app.schema import schema as graphql_schema 
from utils.rbac import get_current_user as fastapi_get_current_user


## 
def setup_google_cloud_credentials():
    """

    """
    try:
        output_file = "service_account.json"
        create_service_account_json(output_file)
        print(f"Google Cloud credentials configured successfully.")
    except Exception as e:
        print(f"Error configuring Google Cloud credentials: {e}")


## adding our api routes 
def include(app):
    app.include_router(api_router)

async def get_graphql_context(request: Request, 
                                  response: FastAPIResponse,
                                  db: Session = Depends(get_db)):
        user_from_dependency: Optional[User] = None 

        try:
            token = request.cookies.get("AccessToken") or request.headers.get("Authorization")
            if token:
                if isinstance(token, str) and token.startswith("Bearer "):
                    token = token.split("Bearer ")[1]
                    try:
                        user_from_dependency = fastapi_get_current_user(request, token, db)
                    except HTTPException as e:
                        user_from_dependency = None 
        except Exception as e:
            print(f"Error getting user from dependency: {e}")
            user_from_dependency = None

        return {
            "request": request,
            "response": response,
            "db": db,
            "current_user": user_from_dependency
        }

graphql_app_router = GraphQLRouter(
    schema=graphql_schema,
    context_getter= get_graphql_context,
    graphiql= settings.SHOW_DOCS == "True"  # Enable GraphiQL interface
  
)



def initial_data_insert():
   
    db = SessionLocal()
    try:
        init_db(db)
        create_super_admin(db)
    finally:
        db.close()

# List of allowed origins
origins = [
    "http://localhost:4200",
    "http://localhost:8080",
    "https://studio.apollographql.com",
    
]

    

def start_application():
    app = FastAPI(docs_url="/", title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_middleware(
    CORSMiddleware,
    # allow_origins= settings.SET_NEW_ORIGIN,
    allow_origins = origins,
    allow_credentials=True,    
    allow_methods=["*"],
    allow_headers=["*"]
    )
    setup_google_cloud_credentials()
    include(app)
    app.include_router(graphql_app_router, prefix="/graphql", tags=["GraphQL"])
    create_tables()
    initial_data_insert()
    return app
app = start_application()





# Custom error handling middleware
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_message = "Validation error occurred"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message+f"{exc}"})



# Generic error handler for all other exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_message = "An unexpected error occurred:\n"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message+f"{exc}"})





@app.exception_handler(json.JSONDecodeError)
async def json_decode_error_handler(request: Request, exc: json.JSONDecodeError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Configuration must be a valid JSON object"},
    )

class IntruderDetectionMiddleware(BaseHTTPMiddleware):
    # Existing middleware - ensure it's compatible or adjust if needed.
    # GraphQL requests will also pass through this.
    # The `db: Session = Depends(get_db)` in __init__ might be problematic for middleware instantiation.
    # Middleware is instantiated once at startup. `Depends` is for path operations.
    # You'll need to manage DB session differently for middleware, e.g., creating a session per request.
    
    # For simplicity, I'll comment out the `db` dependency in __init__
    # and assume related DB operations might need adjustment or be removed from middleware direct use.
    # def __init__(self, app, db: Session = Depends(get_db)): # This line is problematic
    def __init__(self, app): # Corrected
        super().__init__(app)
        # self.db = db # Cannot use Depends here. If DB is needed, resolve it inside dispatch.
    
    async def intruder_info(self, request: Request): # Added self
        client_ip = request.client.host
        headers = request.headers
        user_agent = headers.get("User-Agent")
        mac_address = headers.get("X-MAC-Address")
        location = {}
        try:
            # Consider making this request non-blocking if it's slow
            geo_response = requests.get(f"https://ipinfo.io/{client_ip}/geo", timeout=2)
            geo_response.raise_for_status() # Raise an exception for bad status codes
            location = geo_response.json()
        except requests.RequestException as e:
            print(f"Failed to get geo location for IP {client_ip}: {e}")
            location = {"error": "Failed to retrieve location"}


        intruder_info_dict = { # Renamed variable
            "ip_address": client_ip,
            "mac_address": mac_address,
            "user_agent": user_agent,
            "location": location,
        }
        # settings.intruder_list.append(intruder_info_dict) # Be careful with global lists in async context / multi-worker
        print(f"Intruder detected (info): {intruder_info_dict}") # Changed for clarity
        # Log this to a file or structured log instead of a global list
        await self.log_intruder_info_to_file(intruder_info_dict) # Call instance method
        return intruder_info_dict

    async def log_intruder_info_to_file(self, intruder_data: dict): # Added self and type hint
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d') # Use UTC
        log_file_name = f"intruder_log_{current_date}.txt"
        log_directory = "security/logs/"
        os.makedirs(log_directory, exist_ok=True)
        log_filepath = os.path.join(log_directory, log_file_name)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') # Use UTC
        log_entry = (
            f"{intruder_data.get('ip_address')} | "
            f"{intruder_data.get('mac_address')} | "
            f"{intruder_data.get('user_agent')} | "
            f"{json.dumps(intruder_data.get('location'))} | " # Dump JSON location
            f"{timestamp}\n"
        )

        # File access should be robust, e.g. handle concurrent writes if scaling out
        # For now, simple append:
        try:
            with open(log_filepath, 'a') as file:
                if os.path.getsize(log_filepath) == 0: # Check if file is new/empty
                     file.write("IP Addr | Mac Addr | User Agent | Location | Timestamp\n")
                     file.write("================================================================================\n")
                file.write(log_entry)
        except IOError as e:
            print(f"Error writing to intruder log: {e}")


    async def dispatch(self, request: Request, call_next):
        # Example of how to get a DB session if needed in middleware dispatch
        # db = SessionLocal()
        # try:
        #   pass # use db
        # finally:
        #   db.close()

        response = await call_next(request)
        
        # Example for rate limit handling and account locking (if using FastAPI rate limiter directly)
        # This part of the original code regarding `response.status_code == 429`
        # depends on how rate limiting is implemented. If it's via SlowAPI, that middleware handles responses.
        # The original code tried to use `self.db` which was not correctly initialized.
        # Account locking should ideally be handled closer to the authentication logic.
        
        # If a specific error (e.g., custom auth error) indicates an intrusion attempt, call intruder_info
        # For example, if a 401 is from a failed login:
        # if response.status_code == 401 and "/auth/token" in request.url.path:
        #    await self.intruder_info(request) # Log failed login attempts

        return response







if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, log_level="info", reload = True)
    print("running")