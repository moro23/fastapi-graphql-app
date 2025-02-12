from fastapi_mail import ConnectionConfig,FastMail,MessageSchema
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from config.settings import Settings
from typing import List,Any,Dict
from jinja2 import Environment, select_autoescape, PackageLoader, FileSystemLoader
# from jinja2 import Environment, select_autoescape, PackageLoader
import os
from fastapi import Response, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import UUID4
from domains.auth.models.users import User

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)



class EmailSchema(BaseModel):
    subject: str
    email: List[EmailStr]
    body: Dict[str, str]




class Email:
    def __init__(self, user: User, url: str, email: EmailSchema):

        self.username = user.username
        self.sender = Settings.MAIL_USERNAME
        self.email = email
        self.url = url
       
        

       

    async def sendMailService(data: EmailSchema, template_name: str) -> JSONResponse:
        conf = ConnectionConfig(
            MAIL_USERNAME = Settings.MAIL_USERNAME,
            MAIL_PASSWORD = Settings.MAIL_PASSWORD,
            MAIL_FROM =  Settings.MAIL_FROM,
            MAIL_PORT = Settings.MAIL_PORT,
            MAIL_SERVER = Settings.MAIL_SERVER,
            MAIL_STARTTLS = Settings.MAIL_STARTTLS,
            MAIL_SSL_TLS = Settings.MAIL_SSL_TLS,
            USE_CREDENTIALS = Settings.USE_CREDENTIALS,
            VALIDATE_CERTS = Settings.VALIDATE_CERTS
        )
     
        try: 
            # load the html template
            template = env.get_template(template_name)

        
            ## Render the template with the data provided in 'body'
            html_content = template.render(data.body)

            # html = template.render(
            #     url=self.url,
            #     name=self.name,
            #     email=self.email,
            #     subject=subject
            
        
            # )


            # Define the message options
            message = MessageSchema(
                subject=data.subject,
                recipients=data.email,
                body=html_content,
                subtype="html",

            )

        

            # Send the email using FastMail
            fm = FastMail(conf)
            await fm.send_message(message, template_name=template_name)
            return JSONResponse(status_code=200, content={"message": "Email has been sent."})

        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Failed to send email: {str(e)}")
            return JSONResponse(status_code=500, content={"message": "Failed to send email."})


