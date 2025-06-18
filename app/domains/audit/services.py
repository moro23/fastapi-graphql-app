from sqlachemy.orm import Session 
from .models import AuditLog 
from datetime import datetime, timezone 
from fastapi import Request as FastAPIRequest 
from typing import Optional, Dict, Any 
from uuid import UUID 

def create_audit_log_entry(
        db: Session, action: str, user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None, entity_id: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None, request: Optional[FastAPIRequest] = None
):
    ip_address = request.client.host if request else None 
    user_agent = request.headers.get("user-agent") if request else None 

    audit_entry = AuditLog(
        user_id=user_id,
        action=action, 
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None 
        details=details, 
        ip_address = ip_address,
        user_agent=user_agent 
    )
    db.add(audit_entry)
    db.commit() 
    db.refresh(audit_entry)
    return audit_entry 