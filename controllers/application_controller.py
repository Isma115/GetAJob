from typing import List, Optional
from models.application import Application, PersonalInfo
from utils.database import get_db

class ApplicationController:
    def __init__(self):
        self.db = get_db()

    def add_application(self, application: Application) -> int:
        result = self.db.execute("""
            INSERT INTO applications (company_id, date_applied, status, follow_up_date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            application.company_id,
            application.date_applied,
            application.status,
            application.follow_up_date,
            application.notes
        ))
        return result.lastrowid

    def update_application(self, application: Application) -> bool:
        self.db.execute("""
            UPDATE applications SET
                company_id = ?, date_applied = ?, status = ?,
                follow_up_date = ?, notes = ?
            WHERE id = ?
        """, (
            application.company_id,
            application.date_applied,
            application.status,
            application.follow_up_date,
            application.notes,
            application.id
        ))
        return True

    def delete_application(self, application_id: int) -> bool:
        self.db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        return True

    def get_application(self, application_id: int) -> Optional[Application]:
        row = self.db.fetch_one(
            "SELECT * FROM applications WHERE id = ?", (application_id,)
        )
        return Application.from_row(row)

    def get_all_applications(self) -> List[Application]:
        rows = self.db.fetch_all(
            "SELECT * FROM applications ORDER BY date_applied DESC"
        )
        return [Application.from_row(row) for row in rows]

    def get_applications_by_company(self, company_id: int) -> List[Application]:
        rows = self.db.fetch_all(
            "SELECT * FROM applications WHERE company_id = ? ORDER BY date_applied DESC",
            (company_id,)
        )
        return [Application.from_row(row) for row in rows]

    def get_applications_by_status(self, status: str) -> List[Application]:
        rows = self.db.fetch_all(
            "SELECT * FROM applications WHERE status = ? ORDER BY date_applied DESC",
            (status,)
        )
        return [Application.from_row(row) for row in rows]

    def get_upcoming_follow_ups(self) -> List[Application]:
        rows = self.db.fetch_all("""
            SELECT * FROM applications
            WHERE follow_up_date >= date('now')
            ORDER BY follow_up_date ASC
        """)
        return [Application.from_row(row) for row in rows]

    def get_application_statistics(self) -> dict:
        total = self.db.fetch_one("SELECT COUNT(*) as count FROM applications")
        by_status = self.db.fetch_all("""
            SELECT status, COUNT(*) as count FROM applications GROUP BY status
        """)

        status_dict = {row['status']: row['count'] for row in by_status}

        return {
            'total': total['count'] if total else 0,
            'by_status': status_dict
        }


class PersonalInfoController:
    def __init__(self):
        self.db = get_db()

    def get_personal_info(self) -> Optional[PersonalInfo]:
        row = self.db.fetch_one("SELECT * FROM personal_info LIMIT 1")
        return PersonalInfo.from_row(row)

    def save_personal_info(self, info: PersonalInfo) -> bool:
        existing = self.get_personal_info()
        if existing:
            self.db.execute("""
                UPDATE personal_info SET
                    name = ?, email = ?, phone = ?, linkedin = ?,
                    github = ?, website = ?, address = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                info.name, info.email, info.phone, info.linkedin,
                info.github, info.website, info.address, existing.id
            ))
        else:
            self.db.execute("""
                INSERT INTO personal_info (name, email, phone, linkedin, github, website, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                info.name, info.email, info.phone, info.linkedin,
                info.github, info.website, info.address
            ))
        return True
