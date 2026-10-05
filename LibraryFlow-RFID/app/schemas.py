from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    accession_no: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=250)
    author: str = ""
    isbn: str = ""
    subject: str = ""
    shelf: str = "A-01"
    is_reference: bool = False

class MemberCreate(BaseModel):
    member_no: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=180)
    email: str = ""
    role: str = "student"

class CirculationRequest(BaseModel):
    accession_no: str
    member_no: str

class RenewRequest(BaseModel):
    accession_no: str
    member_no: str

class TagRequest(BaseModel):
    accession_no: str
    tag_id: str = Field(min_length=1, max_length=120)

class GateRequest(BaseModel):
    accession_no: str
    authorised: bool = False
