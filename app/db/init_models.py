
from domains.auth.models.users import APIBase
from db.session import engine


## lets import all our models here so that they are registered with APIBase
from domains.auth.models.users import User
from domains.auth.models.refresh_token import RefreshToken


from domains.faq.models import FAQCategory, FAQItem
from domains.audit.models import AuditLog
from domains.feedback.models import Feedback

def create_tables():
    APIBase.metadata.create_all(bind=engine)

    #APIBase.metadata.drop_all(bind=engine)

   

