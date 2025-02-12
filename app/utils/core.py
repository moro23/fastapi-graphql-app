from datetime import timedelta,datetime
from sqlalchemy.orm import Session
from config import settings
from jose import jwt
import time



#function to encode jwt token
def create_jwt(data:dict, exp:timedelta=None):
    data.update({'exp':datetime.utcnow() + timedelta(minutes=exp if exp else settings.ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=[settings.ALGORITHM])



# function to return the generated tokens (jwt)
def token_response(token: str):
    return {
        "access token": token
    }



# function use for signing the jwt string
def signJWT(user_id: str):
            payload= {
                "user_id": user_id,
                "expire": time.time() + 600
            }
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
            return token_response(token)



#function to decode jwt token
def decode_jwt(token: str, db: Session):
    try:
        decodeJWT = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decodeJWT if decodeJWT['expires'] >= time.time() else None
    except Exception as e:
        return {e}



def raise_exc(loc=None, msg=None, type=None):
    detail = {}
    if loc:
        detail.update({"loc":loc if loc.__class__ in [list, set, tuple] else [loc]})
    if msg:
        detail.update({"msg":msg})
    if msg:
        detail.update({"type":type})
    return [detail] 

def is_pydantic(obj: object):
    """Checks whether an object is pydantic."""
    return type(obj).__class__.__name__ == "ModelMetaclass"


def schema_to_model(schema, exclude_unset=False):
    """Iterates through pydantic schema and parses nested schemas
    to a dictionary containing SQLAlchemy models.
    Only works if nested schemas have specified the Meta.model."""
    parsed_schema = dict(schema)
    try:
        for k,v in parsed_schema.items():
            if isinstance(v, list) and len(v) and is_pydantic(v[0]):
                parsed_schema[k] = [item.Meta.model(**schema_to_model(item)) for item in v]
            elif is_pydantic(v):
                parsed_schema[k] = v.Meta.model(**schema_to_model(v))
    except AttributeError:
        raise AttributeError(f"found nested pydantic model in {schema.__class__} but Meta.model was not specified.")
    
    if exclude_unset:
        parsed_schema = {k: v for k, v in parsed_schema.items() if v is not None}
    
    return parsed_schema

def db_url():
    '''
        current version of sqlalchemy does not support [postgres]:// 
        hence change to postgresql to accomodate
    '''
    db_url = settings.DATABASE_URL
    if db_url.split(':', 1)[0] in ['postgres']:
        db_url = 'postgresql:'+db_url.split(':', 1)[1]
    return db_url