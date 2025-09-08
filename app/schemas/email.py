from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class EmailBase(BaseModel):
    to_email: List[EmailStr] = Field(
        ..., description="List of recipient email addresses"
    )
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body content")
    cc: Optional[List[EmailStr]] = Field(None, description="List of CC email addresses")
    bcc: Optional[List[EmailStr]] = Field(
        None, description="List of BCC email addresses"
    )
    priority: EmailPriority = EmailPriority.NORMAL


class EmailCreate(EmailBase):
    pass


class EmailResponse(EmailBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmailStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
