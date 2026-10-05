from datetime import datetime
from uuid import uuid4
from .base import DeviceAdapter, IlmsAdapter

class MockDeviceAdapter(DeviceAdapter):
    def __init__(self, device_type: str): self.device_type = device_type
    def health(self): return {"device_type": self.device_type, "device_id": f"mock-{self.device_type}", "status": "online (simulated)", "mock": True}
    def read_tags(self, tags=None):
        return {"device": self.health(), "read_at": datetime.utcnow().isoformat(), "tags": tags or [f"EPC-{uuid4().hex[:12].upper()}"], "confirmation": "visual+audible (simulated)"}
    def capture(self): return {"reference": f"mock://camera/{uuid4().hex}.jpg", "mock": True}

class MockIlmsAdapter(IlmsAdapter):
    def checkout(self, accession_no: str, member_no: str):
        return {"adapter": "mock-ncip-sip2-boundary", "protocol": "simulated; not certified NCIP/SIP2", "request_id": str(uuid4()), "accession_no": accession_no, "member_no": member_no, "accepted": True}

class MockNotificationAdapter:
    def send(self, channel: str, recipient: str, message: str):
        return {"channel": channel, "recipient": recipient, "status": "queued (mock)", "message": message, "provider": "mock-provider"}

DEVICES = {name: MockDeviceAdapter(name) for name in ["staff-reader", "handheld-reader", "security-gate", "smart-card", "printer", "camera"]}
ILMS = MockIlmsAdapter()
NOTIFICATIONS = MockNotificationAdapter()
