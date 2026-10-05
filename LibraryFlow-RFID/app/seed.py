from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import Book, Member

SAMPLE_BOOKS = [
    ("ACC-1001", "Clean Code", "Robert C. Martin", "Software Engineering", "CS-01", False, "RFID-A1001"),
    ("ACC-1002", "Introduction to Algorithms", "Thomas H. Cormen et al.", "Algorithms", "CS-01", True, "RFID-A1002"),
    ("ACC-1003", "Database System Concepts", "Silberschatz, Korth, Sudarshan", "Databases", "CS-02", False, "RFID-A1003"),
    ("ACC-1004", "Designing Data-Intensive Applications", "Martin Kleppmann", "Distributed Systems", "CS-02", False, "RFID-A1004"),
    ("ACC-1005", "The Pragmatic Programmer", "Andrew Hunt and David Thomas", "Programming", "CS-03", False, None),
    ("ACC-1006", "Operating System Concepts", "Abraham Silberschatz et al.", "Operating Systems", "CS-04", True, "RFID-A1006"),
    ("ACC-1007", "Computer Networks", "Andrew S. Tanenbaum", "Networking", "CS-04", False, None),
    ("ACC-1008", "Artificial Intelligence: A Modern Approach", "Stuart Russell and Peter Norvig", "AI", "CS-05", False, "RFID-A1008"),
]
SAMPLE_MEMBERS = [
    ("STU-2026-001", "Aarav Sharma", "aarav@example.test", "student", False, 0),
    ("STU-2026-002", "Diya Rao", "diya@example.test", "student", False, 15),
    ("FAC-2026-001", "Dr. Meera Iyer", "meera@example.test", "faculty", False, 0),
    ("STU-2026-003", "Kabir Khan", "kabir@example.test", "student", True, 0),
]

def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Book.id).limit(1)) is None:
            for a,t,author,subject,shelf,ref,tag in SAMPLE_BOOKS:
                db.add(Book(accession_no=a,title=t,author=author,subject=subject,shelf=shelf,is_reference=ref,rfid_tag=tag,tag_status="tagged" if tag else "untagged"))
        if db.scalar(select(Member.id).limit(1)) is None:
            for no,name,email,role,blocked,fine in SAMPLE_MEMBERS:
                db.add(Member(member_no=no,name=name,email=email,role=role,blocked=blocked,fine_balance=fine,smart_card_id=f"CARD-{no}"))
        db.commit()
