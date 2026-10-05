from __future__ import annotations
import json, os, tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from .database import get_db
from .models import Book, Member, Loan, AuditEvent, GateEvent, RfidEvent, MigrationBatch, MigrationStaging
from .schemas import BookCreate, MemberCreate, CirculationRequest, RenewRequest, TagRequest, GateRequest
from .seed import init_db
from .adapters.mocks import DEVICES, ILMS, NOTIFICATIONS
from .services.audit import record
from .services.migration import stage_xlsx, commit_batch, rollback_batch

APP_VERSION = "0.1.0-prototype"
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="LibraryFlow RFID", version=APP_VERSION, description="RFID-enabled library management prototype with isolated mock adapters.", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    stats = {
        "books": db.scalar(select(func.count(Book.id))) or 0,
        "members": db.scalar(select(func.count(Member.id))) or 0,
        "loans": db.scalar(select(func.count(Loan.id)).where(Loan.returned_at.is_(None))) or 0,
        "tagged": db.scalar(select(func.count(Book.id)).where(Book.rfid_tag.is_not(None))) or 0,
        "gate_alerts": db.scalar(select(func.count(GateEvent.id)).where(GateEvent.authorised.is_(False))) or 0,
    }
    books=db.scalars(select(Book).order_by(Book.id.desc()).limit(7)).all()
    members=db.scalars(select(Member).order_by(Member.id.desc()).limit(6)).all()
    events=db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(8)).all()
    return templates.TemplateResponse(request=request,name="index.html",context={"stats":stats,"books":books,"members":members,"events":events,"version":APP_VERSION})

@app.get("/api/health")
def health():
    return {"status":"ok","version":APP_VERSION,"time":datetime.utcnow().isoformat()+"Z","database":"configured","adapters":{k:v.health() for k,v in DEVICES.items()},"mode":"prototype; synthetic data only"}

@app.get("/api/books")
def list_books(q: str="", db: Session=Depends(get_db)):
    stmt=select(Book)
    if q.strip():
        pattern=f"%{q.strip()}%"
        stmt=stmt.where(or_(Book.title.ilike(pattern),Book.author.ilike(pattern),Book.accession_no.ilike(pattern),Book.subject.ilike(pattern),Book.rfid_tag.ilike(pattern)))
    books=db.scalars(stmt.order_by(Book.title).limit(500)).all()
    return [{"id":b.id,"accession_no":b.accession_no,"title":b.title,"author":b.author,"subject":b.subject,"shelf":b.shelf,"is_reference":b.is_reference,"is_available":b.is_available,"rfid_tag":b.rfid_tag,"tag_status":b.tag_status} for b in books]

@app.post("/api/books",status_code=201)
def create_book(payload: BookCreate, db: Session=Depends(get_db)):
    if db.scalar(select(Book).where(Book.accession_no==payload.accession_no)):
        raise HTTPException(409,"Accession number already exists")
    book=Book(**payload.model_dump()); db.add(book); db.flush(); record(db,"book.created","book",book.id,payload.model_dump()); db.commit(); db.refresh(book)
    return {"id":book.id,"accession_no":book.accession_no,"title":book.title}

@app.get("/api/members")
def list_members(q: str="", db: Session=Depends(get_db)):
    stmt=select(Member)
    if q.strip():
        pattern=f"%{q.strip()}%"; stmt=stmt.where(or_(Member.member_no.ilike(pattern),Member.name.ilike(pattern),Member.email.ilike(pattern)))
    return [{"id":m.id,"member_no":m.member_no,"name":m.name,"email":m.email,"role":m.role,"blocked":m.blocked,"fine_balance":float(m.fine_balance or 0),"smart_card_id":m.smart_card_id} for m in db.scalars(stmt.order_by(Member.name).limit(500)).all()]

@app.post("/api/members",status_code=201)
def create_member(payload: MemberCreate, db: Session=Depends(get_db)):
    if db.scalar(select(Member).where(Member.member_no==payload.member_no)): raise HTTPException(409,"Member number already exists")
    member=Member(**payload.model_dump()); db.add(member); db.flush(); record(db,"member.created","member",member.id,payload.model_dump()); db.commit(); return {"id":member.id,"member_no":member.member_no,"name":member.name}

@app.post("/api/circulation/checkout")
def checkout(payload: CirculationRequest, db: Session=Depends(get_db)):
    book=db.scalar(select(Book).where(Book.accession_no==payload.accession_no)); member=db.scalar(select(Member).where(Member.member_no==payload.member_no))
    if not book: raise HTTPException(404,"Book not found")
    if not member: raise HTTPException(404,"Member not found")
    if book.is_reference: raise HTTPException(409,"Reference-only item cannot be checked out")
    if not book.is_available: raise HTTPException(409,"Item is already on loan")
    if member.blocked: raise HTTPException(403,"Member is blocked")
    fine_limit=float(os.getenv("FINE_LIMIT","100.00"))
    if float(member.fine_balance or 0)>fine_limit: raise HTTPException(403,f"Member fine balance exceeds configured limit ({fine_limit:.2f})")
    adapter_response=ILMS.checkout(book.accession_no,member.member_no)
    loan=Loan(book_id=book.id,member_id=member.id,due_date=date.today()+timedelta(days=14)); db.add(loan); book.is_available=False; db.flush()
    record(db,"circulation.checkout","loan",loan.id,{"accession_no":book.accession_no,"member_no":member.member_no,"adapter":adapter_response}); db.commit()
    return {"status":"checked_out","loan_id":loan.id,"accession_no":book.accession_no,"member_no":member.member_no,"due_date":loan.due_date.isoformat(),"integration":adapter_response}

@app.post("/api/circulation/renew")
def renew(payload: RenewRequest, db: Session=Depends(get_db)):
    book=db.scalar(select(Book).where(Book.accession_no==payload.accession_no)); member=db.scalar(select(Member).where(Member.member_no==payload.member_no))
    if not book or not member: raise HTTPException(404,"Book or member not found")
    loan=db.scalar(select(Loan).where(Loan.book_id==book.id,Loan.member_id==member.id,Loan.returned_at.is_(None)).order_by(Loan.id.desc()))
    if not loan: raise HTTPException(404,"No active loan found")
    if member.blocked or float(member.fine_balance or 0)>float(os.getenv("FINE_LIMIT","100.00")): raise HTTPException(403,"Member is not eligible to renew")
    if loan.renewals>=2: raise HTTPException(409,"Renewal limit reached")
    loan.due_date=max(loan.due_date,date.today())+timedelta(days=14); loan.renewals+=1; record(db,"circulation.renewed","loan",loan.id,{"due_date":loan.due_date.isoformat(),"renewals":loan.renewals}); db.commit()
    return {"status":"renewed","loan_id":loan.id,"due_date":loan.due_date.isoformat(),"renewals":loan.renewals}

@app.post("/api/circulation/checkin")
def checkin(payload: CirculationRequest, db: Session=Depends(get_db)):
    book=db.scalar(select(Book).where(Book.accession_no==payload.accession_no)); member=db.scalar(select(Member).where(Member.member_no==payload.member_no))
    if not book or not member: raise HTTPException(404,"Book or member not found")
    loan=db.scalar(select(Loan).where(Loan.book_id==book.id,Loan.member_id==member.id,Loan.returned_at.is_(None)).order_by(Loan.id.desc()))
    if not loan: raise HTTPException(404,"No active loan found")
    loan.returned_at=datetime.utcnow(); book.is_available=True
    overdue=max(0,(date.today()-loan.due_date).days)
    if overdue: member.fine_balance=float(member.fine_balance or 0)+overdue*1.0
    record(db,"circulation.checkin","loan",loan.id,{"overdue_days":overdue,"fine_added":overdue*1.0}); db.commit()
    return {"status":"checked_in","loan_id":loan.id,"overdue_days":overdue,"fine_added":overdue*1.0,"member_fine_balance":float(member.fine_balance or 0)}

@app.get("/api/circulation/loans")
def loans(db: Session=Depends(get_db)):
    items=db.scalars(select(Loan).order_by(Loan.id.desc()).limit(250)).all()
    return [{"loan_id":x.id,"accession_no":x.book.accession_no,"title":x.book.title,"member_no":x.member.member_no,"member_name":x.member.name,"checked_out_at":x.checked_out_at.isoformat(),"due_date":x.due_date.isoformat(),"returned_at":x.returned_at.isoformat() if x.returned_at else None,"renewals":x.renewals} for x in items]

@app.post("/api/rfid/tag")
def tag_item(payload: TagRequest, db: Session=Depends(get_db)):
    book=db.scalar(select(Book).where(Book.accession_no==payload.accession_no))
    if not book: raise HTTPException(404,"Cannot tag: accession record is not present")
    if db.scalar(select(Book).where(Book.rfid_tag==payload.tag_id,Book.id!=book.id)): raise HTTPException(409,"RFID tag is already associated with another item")
    old=book.rfid_tag; book.rfid_tag=payload.tag_id; book.tag_status="tagged"; db.add(RfidEvent(device_type="staff-reader",device_id="mock-staff-reader",tag_id=payload.tag_id,event_type="tag_associated",message=f"{book.accession_no}; previous={old or 'none'}")); record(db,"rfid.tag_associated","book",book.id,{"accession_no":book.accession_no,"tag_id":payload.tag_id,"previous_tag":old}); db.commit()
    return {"status":"tagged","accession_no":book.accession_no,"title":book.title,"rfid_tag":book.rfid_tag,"mock":True}

@app.post("/api/rfid/inventory")
def inventory(shelf: str="CS-01", db: Session=Depends(get_db)):
    shelf_books=db.scalars(select(Book).where(Book.shelf==shelf)).all()
    observed={b.rfid_tag for b in shelf_books if b.rfid_tag}
    result=DEVICES["handheld-reader"].read_tags(sorted(observed))
    records=[]
    for b in shelf_books:
        status="seen" if b.rfid_tag in observed else "missing_or_untagged"
        records.append({"accession_no":b.accession_no,"title":b.title,"expected_shelf":shelf,"observed_tag":b.rfid_tag if b.rfid_tag in observed else None,"status":status})
        db.add(RfidEvent(device_type="handheld-reader",device_id="mock-handheld-reader",tag_id=b.rfid_tag or f"NO-TAG:{b.accession_no}",event_type="inventory_read" if status=="seen" else "inventory_exception",message=status))
    record(db,"rfid.inventory","shelf",shelf,{"item_count":len(records),"seen":sum(x["status"]=="seen" for x in records),"exceptions":sum(x["status"]!="seen" for x in records)})
    db.commit()
    return {"shelf":shelf,"device_result":result,"items":records,"summary":{"expected":len(records),"seen":sum(x["status"]=="seen" for x in records),"exceptions":sum(x["status"]!="seen" for x in records)}}

@app.post("/api/rfid/gate-event")
def gate_event(payload: GateRequest, db: Session=Depends(get_db)):
    book=db.scalar(select(Book).where(Book.accession_no==payload.accession_no))
    if not book: raise HTTPException(404,"Accession number is not present")
    camera=DEVICES["camera"].capture()
    event=GateEvent(accession_no=book.accession_no,authorised=payload.authorised,event_type="passage" if payload.authorised else "unauthorised_removal",cctv_reference=camera["reference"],notification_status="not_required" if payload.authorised else "queued")
    db.add(event); db.flush()
    notification=None
    if not payload.authorised:
        notification=NOTIFICATIONS.send("email","library-security@example.test",f"Mock gate alert for accession {book.accession_no} - {book.title}")
        db.add(RfidEvent(device_type="security-gate",device_id="mock-security-gate",tag_id=book.rfid_tag or book.accession_no,event_type="gate_alert",message=book.accession_no))
        record(db,"gate.unauthorised_removal","gate_event",event.id,{"accession_no":book.accession_no,"camera":camera,"notification":notification})
    else: record(db,"gate.authorised_passage","gate_event",event.id,{"accession_no":book.accession_no})
    db.commit()
    return {"event_id":event.id,"accession_no":book.accession_no,"authorised":event.authorised,"cctv":camera,"notification":notification,"offline_security_bit":"simulated local policy only"}

@app.post("/api/rfid/smart-card-login")
def smart_card_login(card_id: str=Form(...), db: Session=Depends(get_db)):
    member=db.scalar(select(Member).where(Member.smart_card_id==card_id))
    if not member: raise HTTPException(401,"Mock smart-card credential not recognised")
    record(db,"auth.mock_smart_card","member",member.id,{"card_id":card_id,"role":member.role}); db.commit()
    return {"authenticated":True,"mock":True,"member_no":member.member_no,"name":member.name,"role":member.role,"permissions":{"circulation":member.role in ["librarian","admin","faculty"],"administration":member.role=="admin"}}

@app.get("/api/dashboard")
def dashboard(db: Session=Depends(get_db)):
    return {"total_books":db.scalar(select(func.count(Book.id))) or 0,"available_books":db.scalar(select(func.count(Book.id)).where(Book.is_available.is_(True))) or 0,"tagged_items":db.scalar(select(func.count(Book.id)).where(Book.rfid_tag.is_not(None))) or 0,"members":db.scalar(select(func.count(Member.id))) or 0,"blocked_members":db.scalar(select(func.count(Member.id)).where(Member.blocked.is_(True))) or 0,"active_loans":db.scalar(select(func.count(Loan.id)).where(Loan.returned_at.is_(None)) or 0),"overdue_loans":db.scalar(select(func.count(Loan.id)).where(Loan.returned_at.is_(None),Loan.due_date<date.today())) or 0,"gate_events":db.scalar(select(func.count(GateEvent.id))) or 0,"unauthorised_gate_events":db.scalar(select(func.count(GateEvent.id)).where(GateEvent.authorised.is_(False))) or 0,"audit_events":db.scalar(select(func.count(AuditEvent.id))) or 0,"fine_balance_total":float(db.scalar(select(func.sum(Member.fine_balance))) or 0)}

@app.get("/api/reports/audit")
def audit_report(limit: int=100, db: Session=Depends(get_db)):
    events=db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(min(max(limit,1),500))).all()
    return [{"id":e.id,"at":e.at.isoformat(),"actor":e.actor,"action":e.action,"entity_type":e.entity_type,"entity_id":e.entity_id,"details":e.details} for e in events]

@app.get("/api/rfid/devices")
def devices(): return {name:adapter.health() for name,adapter in DEVICES.items()} | {"ilms_adapter":{"status":"mock-ready","boundary":"NCIP 2.0 / SIP2 adapter; protocol exchanges are not certified"},"notifications":{"email":"mock","sms":"mock","print":"mock"}}

@app.post("/api/migration/stage")
async def migration_stage(file: UploadFile=File(...), db: Session=Depends(get_db)):
    if not file.filename or Path(file.filename).suffix.lower() not in {".xlsx"}: raise HTTPException(400,"Upload an .xlsx spreadsheet")
    content=await file.read()
    if len(content)>20*1024*1024: raise HTTPException(413,"File exceeds 20 MB prototype upload limit")
    fd,path=tempfile.mkstemp(suffix=".xlsx")
    try:
        with os.fdopen(fd,"wb") as stream: stream.write(content)
        try: batch=stage_xlsx(db,path,file.filename)
        except ValueError as e: raise HTTPException(400,str(e))
    finally:
        try: os.unlink(path)
        except FileNotFoundError: pass
    return {"batch_id":batch.id,"source_name":batch.source_name,"source_rows":batch.source_rows,"valid_rows":batch.valid_rows,"rejected_rows":batch.rejected_rows,"duplicate_rows":batch.duplicate_rows,"status":batch.status,"errors":json.loads(batch.report_json).get("errors",[])[:100]}

@app.get("/api/migration/batches")
def migration_batches(db: Session=Depends(get_db)):
    return [{"id":b.id,"source_name":b.source_name,"created_at":b.created_at.isoformat(),"source_rows":b.source_rows,"valid_rows":b.valid_rows,"rejected_rows":b.rejected_rows,"duplicate_rows":b.duplicate_rows,"status":b.status} for b in db.scalars(select(MigrationBatch).order_by(MigrationBatch.id.desc())).all()]

@app.get("/api/migration/batches/{batch_id}")
def migration_batch_detail(batch_id: int, db: Session=Depends(get_db)):
    b=db.get(MigrationBatch,batch_id)
    if not b: raise HTTPException(404,"Batch not found")
    rows=db.scalars(select(MigrationStaging).where(MigrationStaging.batch_id==batch_id).order_by(MigrationStaging.row_number)).all()
    return {"id":b.id,"source_name":b.source_name,"status":b.status,"source_rows":b.source_rows,"valid_rows":b.valid_rows,"rejected_rows":b.rejected_rows,"duplicate_rows":b.duplicate_rows,"rows":[{"row_number":r.row_number,"accession_no":r.accession_no,"title":r.title,"status":r.status,"errors":r.errors} for r in rows]}

@app.post("/api/migration/batches/{batch_id}/commit")
def migration_commit(batch_id: int, db: Session=Depends(get_db)):
    try: return commit_batch(db,batch_id)
    except ValueError as e: raise HTTPException(400,str(e))

@app.post("/api/migration/batches/{batch_id}/rollback")
def migration_rollback(batch_id: int, db: Session=Depends(get_db)):
    try: return rollback_batch(db,batch_id)
    except ValueError as e: raise HTTPException(400,str(e))

@app.get("/api/catalog/search")
def catalog_search(q: str="", db: Session=Depends(get_db)):
    return list_books(q,db)
