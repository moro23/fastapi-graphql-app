from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, func
from sqlalchemy.orm import relationship
from db.base_class import APIBase, UUID # Assuming APIBase provides id, created_date, updated_date
from domains.auth.models.users import User # For created_by, updated_by
from datetime import timezone # Import timezone

class FAQCategory(APIBase):
    __tablename__ = "faq_categories"

    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    # faq_items relationship is implicitly via FAQItem.category
    # If you need to access faq_items from category:
    # faq_items = relationship("FAQItem", back_populates="category")

class FAQItem(APIBase):
    __tablename__ = "faq_items"

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("faq_categories.id"), nullable=False)
    category = relationship("FAQCategory", backref="faq_items")

    tags = Column(String, nullable=True) # Simple comma-separated string or JSON string

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by_id], backref="created_faqs")

    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_user = relationship("User", foreign_keys=[updated_by_id], backref="updated_faqs")
    
    is_published = Column(Boolean, default=False, nullable=False)
    publish_date = Column(DateTime(timezone=True), nullable=True) # Store with timezone
    view_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True) # Store with timezone
    # 'created_date' and 'updated_date' from APIBase are already timezone-aware (UTC by default)