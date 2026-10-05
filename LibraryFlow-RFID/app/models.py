from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    accession_no: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    isbn: Mapped[str] = mapped_column(String(30), default="")
    title: Mapped[str] = mapped_column(String(250), index=True)
    author: Mapped[str] = mapped_column(String(180), default="")
    subject: Mapped[str] = mapped_column(String(120), default="")
    shelf: Mapped[str] = mapped_column(String(80), default="A-01")
    is_reference: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    rfid_tag: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True, index=True)
    tag_status: Mapped[str] = mapped_column(String(30), default="untagged")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_no: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180))
    email: Mapped[str] = mapped_column(String(180), default="")
    role: Mapped[str] = mapped_column(String(30), default="student")
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_balance: Mapped[float] = mapped_column(Numeric(10,2), default=0)
    smart_card_id: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)

class Loan(Base):
    __tablename__ = "loans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    checked_out_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    due_date: Mapped[date] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    renewals: Mapped[int] = mapped_column(Integer, default=0)
    book: Mapped[Book] = relationship()
    member: Mapped[Member] = relationship()

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(100), default="demo-admin")
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default="")

class GateEvent(Base):
    __tablename__ = "gate_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    accession_no: Mapped[str] = mapped_column(String(60), index=True)
    event_type: Mapped[str] = mapped_column(String(40), default="unauthorised_removal")
    authorised: Mapped[bool] = mapped_column(Boolean, default=False)
    cctv_reference: Mapped[str] = mapped_column(String(250), default="mock://camera/event.jpg")
    notification_status: Mapped[str] = mapped_column(String(40), default="queued")

class RfidEvent(Base):
    __tablename__ = "rfid_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    device_type: Mapped[str] = mapped_column(String(40))
    device_id: Mapped[str] = mapped_column(String(80))
    tag_id: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(60))
    message: Mapped[str] = mapped_column(Text, default="")

class MigrationBatch(Base):
    __tablename__ = "migration_batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source_name: Mapped[str] = mapped_column(String(250))
    source_rows: Mapped[int] = mapped_column(Integer, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="staged")
    report_json: Mapped[str] = mapped_column(Text, default="{}")

class MigrationStaging(Base):
    __tablename__ = "migration_staging"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("migration_batches.id"), index=True)
    row_number: Mapped[int] = mapped_column(Integer)
    accession_no: Mapped[str] = mapped_column(String(60), default="")
    title: Mapped[str] = mapped_column(String(250), default="")
    author: Mapped[str] = mapped_column(String(180), default="")
    isbn: Mapped[str] = mapped_column(String(30), default="")
    shelf: Mapped[str] = mapped_column(String(80), default="A-01")
    status: Mapped[str] = mapped_column(String(30), default="valid")
    errors: Mapped[str] = mapped_column(Text, default="")
