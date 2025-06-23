import strawberry
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, Request as FastAPIRequest
from .types import FAQCategoryType, FAQItemType, FeedbackType, StrawberryUUID
from .inputs import FAQCategoryInput, FAQItemInput, FAQItemUpdateInput, FeedbackInput
from .permissions import IsAuthenticated, HasRole
from domains.faq.models import FAQCategory as FAQCategoryModel, FAQItem as FAQItemModel
from domains.feedback.models import Feedback as FeedbackModel
from domains.auth.models.users import User as UserModel # For current_user type hint
from domains.audit.services import create_audit_log_entry # Audit log service
from db.session import get_db # FastAPI dependency
# from utils.rbac import get_current_user # FastAPI dependency, or use info.context
from uuid import UUID
from datetime import datetime, timezone


# Helper for audit logging in mutations
def _log_action(info: strawberry.Info, action: str, entity_type: Optional[str] = None, entity_id: Optional[Any] = None, details: Optional[dict] = None):
    db: Session = info.context["db"]
    current_user: Optional[UserModel] = info.context.get("current_user")
    request: FastAPIRequest = info.context["request"]
    
    create_audit_log_entry(
        db=db,
        user_id=current_user.id if current_user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        request=request
    )

@strawberry.type 
class Mutation:
    @strawberry.mutation(permissions_classes=[IsAuthenticated, HasRole(role_name="admin")])
    async def create_faq_category(self, info: strawberry.types.Info, input: FAQCategoryInput) -> FAQCategoryType:
        """Create a new FAQ category."""
        db: Session = info.context["db"]
        category = FAQCategoryModel(**input.dict())
        db.add(category)
        db.commit()
        db.refresh(category)
        
        # Log the action
        _log_action(info, "create", entity_type="FAQCategory", entity_id=category.id, details=input.dict())
        
        return FAQCategoryType.from_orm(category)

    @strawberry.mutation(permissions_classes=[IsAuthenticated, HasRole(role_name="admin")])
    async def update_faq_category(self, info: strawberry.types.Info, id: StrawberryUUID, input: FAQCategoryInput) -> FAQCategoryType:
        """Update an existing FAQ category."""
        db: Session = info.context["db"]
        category = db.query(FAQCategoryModel).filter(FAQCategoryModel.id == id).first()
        if not category:
            raise ValueError("FAQ Category not found")
        
        for key, value in input.dict().items():
            setattr(category, key, value)
        
        db.commit()
        db.refresh(category)
        
        # Log the action
        _log_action(info, "update", entity_type="FAQCategory", entity_id=category.id, details=input.dict())
        
        return FAQCategoryType.from_orm(category)

    @strawberry.mutation(permissions_classes=[IsAuthenticated, HasRole(role_name="admin")])
    async def delete_faq_category(self, info: strawberry.types.Info, id: StrawberryUUID) -> bool:
        """Delete an existing FAQ category."""
        db: Session = info.context["db"]
        category = db.query(FAQCategoryModel).filter(FAQCategoryModel.id == id).first()
        if not category:
            raise ValueError("FAQ Category not found")
        
        db.delete(category)
        db.commit()
        
        # Log the action
        _log_action(info, "delete", entity_type="FAQCategory", entity_id=id)
        
        return True

    @strawberry.mutation(permissions_classes=[HasRole(["Super Admin", "Editor"])])
    async def create_faq_item(self, info: strawberry.types.Info, input: FAQItemInput, db: Session = Depends(get_db)) -> FAQItemType:
        """Create a new FAQ item."""
        current_user: Optional[UserModel] = info.context.get("current_user")
        if not current_user:
            raise ValueError("User must be authenticated to create FAQ items.")
        
        category = db.query(FAQCategoryModel).filter(FAQCategoryModel.id == UUID(str(input.category_id))).first()
        if not category:
            raise ValueError("FAQ Category not found")
        
        faq_item = FAQItemModel(
            question=input.question,
            answer=input.answer,
            tags=input.tags,
            is_published=input.is_published,
            category_id=category.id,
            created_by_user_id=current_user.id,
            updated_by_id=current_user.id,
            published_date=datetime.now(timezone.utc) if (input.is_published or False)  else None
            )
        
        # item = FAQItemModel(**input.dict(), created_by_user_id=current_user.id)
        db.add(faq_item)
        db.commit()
        db.refresh(faq_item)
        
        # Log the action
        _log_action(info, "create", entity_type="FAQItem", entity_id=faq_item.id, details=input.dict())
        
        return FAQItemType.from_orm(faq_item)
    

    @strawberry.mutation(permission_classes=[HasRole(["Super Admin", "Editor"])])
    async def update_faq_item(self, info: strawberry.Info, id: StrawberryUUID, input: FAQItemUpdateInput, db: Session = Depends(get_db)) -> Optional[FAQItemType]:
        current_user: UserModel = info.context["current_user"]
        faq_item = db.query(FAQItemModel).filter(FAQItemModel.id == id).first()
        if not faq_item:
            return None

        update_data = input.__dict__ # Or input.to_pydantic() if using Strawberry Pydantic features
        original_values = {
            "question": faq_item.question, "answer": faq_item.answer, "is_published": faq_item.is_published
        } # For audit log

        for field, value in update_data.items():
            if value is not None: # Only update fields that are provided
                if field == "category_id" and value:
                    # Verify category exists
                    category = db.query(FAQCategoryModel).filter(FAQCategoryModel.id == UUID(str(value))).first()
                    if not category:
                        raise ValueError(f"Category with id {value} not found.")
                    setattr(faq_item, field, category.id)
                elif field == "is_published" and value == True and faq_item.is_published == False:
                    faq_item.publish_date = datetime.now(timezone.utc)
                    setattr(faq_item, field, value)
                elif field == "is_published" and value == False:
                    faq_item.publish_date = None # Unpublishing
                    setattr(faq_item, field, value)
                else:
                     setattr(faq_item, field, value)
        
        faq_item.updated_by_id = current_user.id
        # APIBase should handle updated_date automatically if configured, or manually:
        faq_item.updated_date = datetime.now(timezone.utc)

        db.commit()
        db.refresh(faq_item)
        _log_action(info, "UPDATE_FAQ_ITEM", "FAQItem", faq_item.id, {"changes": update_data, "original": original_values})
        return FAQItemType.from_orm(faq_item)

    @strawberry.mutation(permission_classes=[HasRole(["Super Admin", "Editor"])])
    async def delete_faq_item(self, info: strawberry.Info, id: StrawberryUUID, db: Session = Depends(get_db)) -> bool:
        faq_item = db.query(FAQItemModel).filter(FAQItemModel.id == id).first()
        if not faq_item:
            return False
        
        # Soft delete or hard delete based on policy. For now, hard delete.
        # Consider impact on feedback linked to this FAQ.
        # For auditability, a soft delete (is_deleted=True) is often better.
        # Let's do a hard delete for simplicity here.
        question = faq_item.question # For audit log
        db.delete(faq_item)
        db.commit()
        _log_action(info, "DELETE_FAQ_ITEM", "FAQItem", id, {"question": question})
        return True

    @strawberry.mutation # Open to all for submitting feedback
    async def submit_feedback(self, info: strawberry.Info, input: FeedbackInput, db: Session = Depends(get_db)) -> FeedbackType:
        current_user: Optional[UserModel] = info.context.get("current_user") # Optional
        
        faq_item_instance = None
        if input.faq_item_id:
            faq_item_instance = db.query(FAQItemModel).filter(FAQItemModel.id == UUID(str(input.faq_item_id))).first()
            if not faq_item_instance:
                raise ValueError("Associated FAQ item not found.")

        feedback = FeedbackModel(
            comment=input.comment,
            faq_item_id=faq_item_instance.id if faq_item_instance else None,
            rating=input.rating,
            contact_email=input.contact_email,
            user_id=current_user.id if current_user else None,
            status="new"
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        _log_action(info, "SUBMIT_FEEDBACK", "Feedback", feedback.id, {"comment_excerpt": feedback.comment[:50]})
        return FeedbackType.from_orm(feedback)
        
    @strawberry.mutation(permission_classes=[HasRole(["Super Admin", "Editor"])])
    async def update_feedback_status(self, info: strawberry.Info, id: StrawberryUUID, status: str, db: Session = Depends(get_db)) -> Optional[FeedbackType]:
        feedback = db.query(FeedbackModel).filter(FeedbackModel.id == id).first()
        if not feedback:
            return None
        
        original_status = feedback.status
        feedback.status = status
        feedback.updated_date = datetime.now(timezone.utc) # Manually if APIBase doesn't auto-update on all changes
        db.commit()
        db.refresh(feedback)
        _log_action(info, "UPDATE_FEEDBACK_STATUS", "Feedback", feedback.id, {"old_status": original_status, "new_status": status})
        return FeedbackType.from_orm(feedback)
