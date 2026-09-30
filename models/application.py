from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Application:
    id: Optional[int] = None
    company_id: int = 0
    date_applied: str = ""
    status: str = "applied"
    follow_up_date: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'date_applied': self.date_applied,
            'status': self.status,
            'follow_up_date': self.follow_up_date,
            'notes': self.notes,
            'created_at': self.created_at
        }

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            company_id=row['company_id'],
            date_applied=row['date_applied'],
            status=row['status'],
            follow_up_date=row['follow_up_date'],
            notes=row['notes'],
            created_at=row['created_at']
        )

@dataclass
class PersonalInfo:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    address: str = ""

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'linkedin': self.linkedin,
            'github': self.github,
            'website': self.website,
            'address': self.address
        }

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            phone=row['phone'],
            linkedin=row['linkedin'],
            github=row['github'],
            website=row['website'],
            address=row['address']
        )
