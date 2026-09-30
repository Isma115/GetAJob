from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Company:
    id: Optional[int] = None
    name: str = ""
    job_title: str = ""
    job_type: str = ""
    location: str = ""
    work_mode: str = ""
    salary_min: str = ""
    salary_max: str = ""
    company_size: str = ""
    industry: str = ""
    job_url: str = ""
    notes: str = ""
    status: str = "wishlist"
    contacted: bool = False
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'job_title': self.job_title,
            'job_type': self.job_type,
            'location': self.location,
            'work_mode': self.work_mode,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'company_size': self.company_size,
            'industry': self.industry,
            'job_url': self.job_url,
            'notes': self.notes,
            'status': self.status,
            'contacted': self.contacted,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            job_title=row['job_title'],
            job_type=row['job_type'],
            location=row['location'],
            work_mode=row['work_mode'],
            salary_min=row['salary_min'],
            salary_max=row['salary_max'],
            company_size=row['company_size'],
            industry=row['industry'],
            job_url=row['job_url'],
            notes=row['notes'],
            status=row['status'],
            contacted=bool(row['contacted']),
            contact_name=row['contact_name'],
            contact_email=row['contact_email'],
            contact_phone=row['contact_phone'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
