from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone
from uuid import UUID as UUID_V
from functools import reduce
from typing import Any
import typing as t
import inflect
import uuid



class_registry: t.Dict = {}


def change_case(str):
    return reduce(lambda x, y: x + ('_' if y.isupper() else '') + y, str).lower()


@as_declarative(class_registry=class_registry)
class Base:
    id: Any
    __name__: str
    
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        camel_check = change_case(cls.__name__)
        p = inflect.engine()
        return p.plural(camel_check.lower())
    





@as_declarative(class_registry=class_registry)
class APIBase(Base):

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True,index=True, nullable=False, default=uuid.uuid4)

    created_date = Column(DateTime, default=datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=datetime.now(timezone.utc))

