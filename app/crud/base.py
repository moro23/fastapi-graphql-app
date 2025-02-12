from typing import Any,Dict,Generic,List,Optional,Type,TypeVar,Union
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from utils.security import pwd_context
from sqlalchemy import and_,select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import inspect
from db.base_class import Base
from pydantic import UUID4
from uuid import UUID
import Levenshtein
import sys




ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):  # 1

    def __init__(self, model: Type[ModelType]):  # 2
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    

    def get_by_email(self, db: Session, email: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.email == email).first()
    

    def get_all(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    async def read(self, db: Session, search: str = None, value: str = None, skip: int = 0, limit: int = 100):
        base = db.query(self.model)
        if search and value:
            try:
                base = base.filter(
                    self.model.__table__.c[search].like("%" + value + "%"))
            except KeyError:
                return base.offset(skip).limit(limit).all()
        return base.offset(skip).limit(limit).all()

    async def iread(self, db: Session, search: str = None, value: str = None, skip: int = 0, limit: int = 100):
        base = db.query(self.model)
        if search and value:
            try:
                base = base.filter(
                    self.model.__table__.c[search].ilike("%" + value + "%"))
            except KeyError:
                return base.offset(skip).limit(limit).all()
        return base.offset(skip).limit(limit).all()
    

    async def read_by_id(self, id, db: Session):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all_by_ids(self, db: Session, ids: List[Any]) -> Optional[List[ModelType]]:
        if ids is None:
            ids = []
        return db.query(self.model).filter(self.model.id.in_(ids)).all()

    def get_by_id(self, id: Any, db: Session) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_name(self, db: Session, name: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.name == name).first()
    

    def get_by_reset_password_token(self, db: Session, token: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.reset_password_token == token).first()
    



    ## function to update admin or users password base on token after reseting password
    def update_user_after_reset_password(self,db: Session,*,db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]):
        
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj.password = pwd_context.hash(obj_in.password)
        db_obj.reset_password_token = None
        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj
    

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:

        try:
            if not obj_in:
                return None
            # from datetime import datetime
            # obj_in.created_at = datetime.utcnow()
            # obj_in.updated_at = obj_in.created_at

            obj_in_data = obj_in.dict()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409, detail="{}".format(sys.exc_info()[1]))

        except Exception as ex:
            db.rollback()
            import traceback

            raise HTTPException(status_code=500, detail="{}: {}".format(
                sys.exc_info()[0], sys.exc_info()[1]))

    def _update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:

        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
    #     obj_data = jsonable_encoder(db_obj)
    #     update_data = obj_in.dict(exclude_unset=True)
    #     try:
    #         for field in obj_data:
    #             if field in update_data:
    #                 setattr(db_obj, field, update_data[field])
    #         db.add(db_obj)
    #         db.commit()
    #         db.refresh(db_obj)
    #         return db_obj
    #     except Exception as ex:
    #         db.rollback()
    #         import traceback
    #         print(''.join(traceback.TracebackException.from_exception(ex).format()))
    #         raise HTTPException(status_code=500, detail="{}: {}".format(
    #             sys.exc_info()[0], sys.exc_info()[1])
    #                             )


    def get_model_by_id(db: Session, model, id: Any) -> Optional[ModelType]:
        return db.query(model).filter(model.id == id).first()

    

    def get_unique_indexed_fields(model: Type[Any]) -> Dict[str, bool]:
        """ Get unique and indexed fields for a given model. """
        mapper = inspect(model)
        unique_fields = [col.name for col in mapper.columns if col.unique]
        indexed_fields = [col.name for col in mapper.columns if col.index]
        return unique_fields + indexed_fields

    # def calculate_similarity(data1: str, data2: str) -> float:
    #     """ Calculate the Levenshtein similarity between two strings. """
    #     return Levenshtein.ratio(data1.lower(), data2.lower())

    @staticmethod
    def calculate_similarity(data1: Any, data2: Any) -> float:
        """ Calculate the similarity between two pieces of data. """
        if isinstance(data1, str) and isinstance(data2, str):
            return Levenshtein.ratio(data1.lower(), data2.lower())
        elif isinstance(data1, dict) and isinstance(data2, dict):
            keys1, keys2 = set(data1.keys()), set(data2.keys())
            common_keys = keys1 & keys2
            similarities = []
            for key in common_keys:
                similarities.append(CRUDBase.calculate_similarity(data1[key], data2[key]))
            if similarities:
                return sum(similarities) / len(similarities)
        elif isinstance(data1, (int, float, bool)) and isinstance(data2, (int, float, bool)):
            return 1.0 if data1 == data2 else 0.0
        elif isinstance(data1, UUID) and isinstance(data2, UUID):
            return 1.0 if data1 == data2 else 0.0
        return 0.0
    



    @staticmethod
    def is_similar(data1: Dict[str, Any], data2: Dict[str, Any], threshold: float = 0.90) -> bool:
        """ Check if data1 values are similar to data2 values based on a given threshold. """
        similarities = []
        for key in data1:
            if key in data2:
                similarity = CRUDBase.calculate_similarity(data1[key], data2[key])
                similarities.append(similarity)
        
        if similarities:
            average_similarity = sum(similarities) / len(similarities)
            return average_similarity >= threshold
        return False



    def is_unique_or_similar_to_current(db: Session, model: Type, payload: Dict[str, Any], row_id: Any) -> bool:
        """
        Check if the payload is unique or similar to the existing row data in the database.

        Parameters:
        - db: SQLAlchemy session object.
        - model: The SQLAlchemy model class.
        - payload: Data payload to check.
        - row_id: ID of the current row being updated.

        Returns:
        - True if the payload is similar to the current row data or unique.
        - False otherwise.
        """
        # Fetch current data for the given row ID
        current_row = db.query(model).filter_by(id=row_id).first()
        if not current_row:
            raise ValueError(f"No row found with id {row_id}")

        # Get unique columns for the model
        unique_columns = [col.name for col in inspect(model).columns if col.unique]
        
        # Build a filter to exclude the current row and find similar entries
        filters = [getattr(model, col) == payload.get(col) for col in unique_columns if col in payload]
        if filters:
            similar_rows = db.query(model).filter(*filters).filter(model.id != row_id).all()
            if similar_rows:
                return False

        # Validate uniqueness across all existing rows
        for col in unique_columns:
            if col in payload:
                existing_rows = db.query(model).filter(getattr(model, col) == payload[col]).filter(model.id != row_id).all()
                if existing_rows:
                    return False

        return True


    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        try:
            if not CRUDBase.is_unique_or_similar_to_current(db, self.model, update_data, db_obj.id):
                raise HTTPException(status_code=400, detail="The incoming data is similar to an existing row")

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except HTTPException as e:
            raise e
        except Exception as ex:
            db.rollback()
            import traceback
            raise HTTPException(status_code=500, detail="{}: {}".format(sys.exc_info()[0], sys.exc_info()[1]))


    def remove(self, db: Session, *, id: UUID4) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

    async def filter_range(self, db: Session, skip: int = 0, limit: int = 100, search: str = None,
                           lower_boundary: float = 0, upper_boundary: float = 0):
        try:
            base = db.query(self.model)
            if lower_boundary and upper_boundary:
                try:
                    base = base.filter(and_(
                        self.model.__table__.c[search] <= upper_boundary,
                        self.model.__table__.c[search] >= lower_boundary
                    ))
                except KeyError:
                    return base.offset(skip).limit(limit).all()
            return base.offset(skip).limit(limit).all()
        except:
            raise HTTPException(
                status_code=500, detail="{}".format(sys.exc_info()[1]))
    


#from .history.backend.app.crud.base_20240730090819 import CRUDBase

def is_name_similar(name1, name2, threshold=0.9):
    similarity = Levenshtein.ratio(name1.lower(), name2.lower())
    return similarity >= threshold
