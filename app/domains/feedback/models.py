from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import relationship
from db.base_class import APIBase, UUID
from domains.faq.models import FAQItem
from domains.auth.models.users import User
from datetime import timezone # Import timezone

class Feedback(APIBase):
    __tablename__ = "feedback"

    faq_item_id = Column(UUID(as_uuid=True), ForeignKey("faq_items.id"), nullable=True)
    faq_item = relationship("FAQItem", backref="feedbacks") # Changed backref to plural

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="feedbacks_submitted") # Changed backref to plural
    
    rating = Column(Integer, nullable=True) 
    comment = Column(Text, nullable=False)
    contact_email = Column(String(255), nullable=True) 
    status = Column(String(50), default="new", nullable=False) # e.g., "new", "reviewed", "resolved"
    # 'created_date' from APIBase serves as submitted_at