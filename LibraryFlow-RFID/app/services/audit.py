import json
from sqlalchemy.orm import Session
from ..models import AuditEvent

def record(db: Session, action: str, entity_type: str, entity_id: str, details: dict | str = "", actor: str = "demo-admin"):
    if not isinstance(details, str): details = json.dumps(details, ensure_ascii=False, sort_keys=True)
    db.add(AuditEvent(actor=actor, action=action, entity_type=entity_type, entity_id=str(entity_id), details=details))
