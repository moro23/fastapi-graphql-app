from domains.auth.models.refresh_token import APIBase
from domains.auth.models.users import APIBase
from db.session import engine


def create_tables():
    APIBase.metadata.create_all(bind=engine)

    #APIBase.metadata.drop_all(bind=engine)

   

