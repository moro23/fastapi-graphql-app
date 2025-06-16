from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from db.base_class import APIBase, UUID
from domains.auth.models.users import User
from datetime import timezone # Import timezone

class AuditLog(APIBase):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="audit_logs_entries") # Changed backref
    
    action = Column(String(255), nullable=False) 
    entity_type = Column(String(100), nullable=True) 
    entity_id = Column(String(36), nullable=True) 
    
    details = Column(JSON, nullable=True) 
    ip_address = Column(String(45), nullable=True) 
    user_agent = Column(Text, nullable=True)
    # 'created_date' from APIBase serves as timestamp