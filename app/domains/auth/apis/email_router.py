from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from typing import List
from services.email_service import EmailSchema,Email 


email_router = APIRouter(
    prefix="",
    tags=["Email Service"],
    responses={404: {"description": "Not found"}},
) 


## Endpoint for sending email aynchronously 
@email_router.post("/send-email")
async def send_email_async(data: EmailSchema):
    return await Email.sendMailService(data, template_name="welcome_email.html")