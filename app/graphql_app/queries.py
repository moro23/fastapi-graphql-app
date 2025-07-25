import strawberry
from typing import List, Optional, Annotated
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_, and_
from fastapi import Depends
# import strawberry.fastapi.deps as strawberry_deps 
from .types import FAQCategoryType, FAQItemType, FeedbackType, AuditLogType, UserType, RoleType, StrawberryUUID
from .permissions import IsAuthenticated, HasRole
from domains.faq.models import FAQCategory as FAQCategoryModel, FAQItem as FAQItemModel
from domains.feedback.models import Feedback as FeedbackModel
from domains.audit.models import AuditLog as AuditLogModel
from domains.auth.models.users import User as UserModel
from domains.auth.models.roles import Role as RoleModel
from db.session import get_db # FastAPI dependency
from utils.rbac import get_current_user # FastAPI dependency
from uuid import UUID
from datetime import datetime, timezone

@strawberry.type 
class Query: 
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info:strawberry.Info) -> Optional[UserType]:
        """Get the current authenticated user."""
        current_user = get_current_user(info)
        if not current_user:
            return None
        return UserType.from_orm(current_user)
    
    @strawberry.field
    async def faq_item(self, id: StrawberryUUID, info: strawberry.Info )-> Optional[FAQItemType]:
        db: Session = info.context["db"]
        item = db.query(FAQItemModel).options(
            selectinload(FAQItemModel.category),
            selectinload(FAQItemModel.created_by_user)
        ).filter(FAQItemModel.id == id).first()
        if item:
             # Update view count and last accessed (simplified)
            item.view_count = (item.view_count or 0) + 1
            item.last_accessed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(item)
            return FAQItemType.from_orm(item)
        return None

    @strawberry.field
    async def list_faq_items(
        self, 
        info: strawberry.Info,
        category_id: Optional[StrawberryUUID] = None, 
        search_term: Optional[str] = None,
        published_only: Optional[bool] = True,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        
    ) -> List[FAQItemType]:
        db: Session = info.context["db"]
        query = db.query(FAQItemModel).options(
            selectinload(FAQItemModel.category),
            selectinload(FAQItemModel.created_by_user)
        )
        if published_only:
            query = query.filter(FAQItemModel.is_published == True)
        if category_id:
            query = query.filter(FAQItemModel.category_id == category_id)
        if search_term:
            query = query.filter(
                or_(
                    FAQItemModel.question.ilike(f"%{search_term}%"),
                    FAQItemModel.answer.ilike(f"%{search_term}%"),
                    FAQItemModel.tags.ilike(f"%{search_term}%") # Basic tag search
                )
            )
        items = query.order_by(FAQItemModel.created_date.desc()).limit(limit).offset(offset).all()
        return [FAQItemType.from_orm(item) for item in items]

    @strawberry.field
    async def list_faq_categories(self, info: strawberry.Info) -> List[FAQCategoryType]:
        db: Session = info.context["db"]
        categories = db.query(FAQCategoryModel).all()
        return [FAQCategoryType.from_orm(cat) for cat in categories]

    # Admin/Protected queries
    @strawberry.field()
    async def list_all_feedback(
        self, 
        info: strawberry.Info,
        faq_item_id: Optional[StrawberryUUID] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
    ) -> List[FeedbackType]:
        db: Session = info.context["db"]
        query = db.query(FeedbackModel).options(selectinload(FeedbackModel.faq_item), selectinload(FeedbackModel.user))
        if faq_item_id:
            query = query.filter(FeedbackModel.faq_item_id == faq_item_id)
        feedbacks = query.order_by(FeedbackModel.created_date.desc()).limit(limit).offset(offset).all()
        return [FeedbackType.from_orm(fb) for fb in feedbacks]

    @strawberry.field()
    async def list_audit_logs(
        self, 
        info: strawberry.Info,
        user_id: Optional[StrawberryUUID] = None,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
    ) -> List[AuditLogType]:
        db: Session = info.context["db"]
        query = db.query(AuditLogModel).options(selectinload(AuditLogModel.user))
        if user_id:
            query = query.filter(AuditLogModel.user_id == user_id)
        if action:
            query = query.filter(AuditLogModel.action.ilike(f"%{action}%"))
        if entity_type:
            query = query.filter(AuditLogModel.entity_type == entity_type)
        logs = query.order_by(AuditLogModel.created_date.desc()).limit(limit).offset(offset).all()
        return [AuditLogType.from_orm(log) for log in logs]
        
    @strawberry.field()
    async def list_users(self, info: strawberry.Info) -> List[UserType]:
        db: Session = info.context["db"]
        users = db.query(UserModel).options(selectinload(UserModel.role)).all()
        return [UserType.from_orm(user) for user in users]

    @strawberry.field()
    async def list_roles(self, info: strawberry.Info) -> List[RoleType]:
        db: Session = info.context["db"]
        roles = db.query(RoleModel).all()
        return [RoleType.from_orm(role) for role in roles]
