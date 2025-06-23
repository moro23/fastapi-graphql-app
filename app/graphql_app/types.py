import strawberry 
from typing import List, Optional, TYPE_CHECKING, NewType 
from datetime import datetime 
from pydantic import UUID4 
from domains.auth.models import User as UserModel 
from domains.auth.models.roles import Role as RoleModel 
from domains.faq.models import FAQCategory as FAQCategoryModel,  FAQItem as FAQItemModel
from domains.feedback.models import Feedback as FeedbackModel 
from domains.audit.models import AuditLog as AuditLogModel 
from strawberry.fastapi import BaseContext 
from sqlalchemy.orm import Session, selectinload 
from db.session import get_db 
from fastapi import Depends 

## Custom Strawberry ID type for UUIDs if needed, or map to str/strawberry.ID
StrawberryUUID = strawberry.scalar(
    NewType("StrawberryUUID", UUID4),
    serializer=lambda v: str(v) 
    parse_value=lambda v: UUID4(v)
)

## Forward declaration for circular dependencies if any 
if TYPE_CHECKING:
    pass 

@strawberry.type
class UserType: 
    id: StrawberryUUID
    username: str 
    email: str 
    is_active: bool

    @strawberry.field
    async def role(self, info: strawberry.info) -> Optional["RoleType"]: 
        db: Session = info.context["db"]
        user_model = db.query(UserModel).options(selectinload(UserModel.role)).filter(UserModel.id == self.id).first()
        if user_model and user_model.role:
            return RoleType.from_orm(user_model.role)
        return None

    @classmethod
    def from_orm(cls, user: UserModel) -> "UserType":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    

@strawberry.type
class RoleType:
    id: StrawberryUUID
    name: str

    @classmethod
    def from_orm(cls, model: RoleModel):
        return cls(id=model.id, name=model.name)


@strawberry.type
class FAQCategoryType:
    id: StrawberryUUID
    name: str
    description: Optional[str]
    # created_date: datetime # from APIBase
    # updated_date: datetime # from APIBase

    @strawberry.field
    async def faq_items(self, info: strawberry.Info) -> List["FAQItemType"]:
        db: Session = info.context["db"]
        # Example of loading related items; Strawberry-SQLAlchemy integration can simplify this
        category_model = db.query(FAQCategoryModel).options(selectinload(FAQCategoryModel.faq_items)).filter(FAQCategoryModel.id == self.id).first()
        if category_model:
            return [FAQItemType.from_orm(item) for item in category_model.faq_items]
        return []

    @classmethod
    def from_orm(cls, model: FAQCategoryModel):
        return cls(
            id=model.id,
            name=model.name,
            description=model.description
            # created_date=model.created_date,
            # updated_date=model.updated_date,
        )


@strawberry.type
class FAQItemType:
    id: StrawberryUUID
    question: str
    answer: str
    tags: Optional[str]
    is_published: bool
    publish_date: Optional[datetime]
    view_count: int
    last_accessed_at: Optional[datetime]
    # created_date: datetime
    # updated_date: datetime

    @strawberry.field
    async def category(self, info: strawberry.Info) -> FAQCategoryType:
        db: Session = info.context["db"]
        item_model = db.query(FAQItemModel).options(selectinload(FAQItemModel.category)).filter(FAQItemModel.id == self.id).first()
        # This is inefficient if loading many items (N+1). Dataloaders would be better.
        # Or, ensure category is eager-loaded when FAQItem is fetched.
        if item_model and item_model.category:
             return FAQCategoryType.from_orm(item_model.category)
        # This should not happen if category_id is non-nullable and data is consistent
        raise ValueError("Category not found for FAQ item")


    @strawberry.field
    async def created_by(self, info: strawberry.Info) -> Optional[UserType]:
        db: Session = info.context["db"]
        item_model = db.query(FAQItemModel).options(selectinload(FAQItemModel.created_by_user)).filter(FAQItemModel.id == self.id).first()
        if item_model and item_model.created_by_user:
            return UserType.from_orm(item_model.created_by_user)
        return None
    
    # Similar for updated_by if needed

    @classmethod
    def from_orm(cls, model: FAQItemModel):
        return cls(
            id=model.id,
            question=model.question,
            answer=model.answer,
            tags=model.tags,
            is_published=model.is_published,
            publish_date=model.publish_date,
            view_count=model.view_count,
            last_accessed_at=model.last_accessed_at,
            # created_date=model.created_date,
            # updated_date=model.updated_date,
        )

@strawberry.type
class FeedbackType:
    id: StrawberryUUID
    comment: str
    rating: Optional[int]
    contact_email: Optional[str]
    status: str
    # created_date: datetime # submitted_at

    @strawberry.field
    async def faq_item(self, info: strawberry.Info) -> Optional[FAQItemType]:
        db: Session = info.context["db"]
        feedback_model = db.query(FeedbackModel).options(selectinload(FeedbackModel.faq_item)).filter(FeedbackModel.id == self.id).first()
        if feedback_model and feedback_model.faq_item:
            return FAQItemType.from_orm(feedback_model.faq_item)
        return None

    @strawberry.field
    async def user(self, info: strawberry.Info) -> Optional[UserType]:
        db: Session = info.context["db"]
        feedback_model = db.query(FeedbackModel).options(selectinload(FeedbackModel.user)).filter(FeedbackModel.id == self.id).first()
        if feedback_model and feedback_model.user:
            return UserType.from_orm(feedback_model.user)
        return None

    @classmethod
    def from_orm(cls, model: FeedbackModel):
        return cls(
            id=model.id,
            comment=model.comment,
            rating=model.rating,
            contact_email=model.contact_email,
            status=model.status,
            # created_date=model.created_date
        )

@strawberry.type
class AuditLogType:
    id: StrawberryUUID
    action: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    details: Optional[strawberry.scalars.JSON] # Strawberry has a built-in JSON scalar
    ip_address: Optional[str]
    user_agent: Optional[str]
    # created_date: datetime # timestamp

    @strawberry.field
    async def user(self, info: strawberry.Info) -> Optional[UserType]:
        db: Session = info.context["db"]
        log_model = db.query(AuditLogModel).options(selectinload(AuditLogModel.user)).filter(AuditLogModel.id == self.id).first()
        if log_model and log_model.user:
            return UserType.from_orm(log_model.user)
        return None

    @classmethod
    def from_orm(cls, model: AuditLogModel):
        return cls(
            id=model.id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            details=model.details,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            # created_date=model.created_date
        ) 