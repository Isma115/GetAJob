from typing import List, Optional
from models.company import Company
from utils.database import get_db

class CompanyController:
    def __init__(self):
        self.db = get_db()

    def add_company(self, company: Company) -> int:
        result = self.db.execute("""
            INSERT INTO companies (name, job_title, job_type, location, work_mode,
                salary_min, salary_max, company_size, industry, job_url, notes, status, contacted,
                contact_name, contact_email, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company.name, company.job_title, company.job_type, company.location,
            company.work_mode, company.salary_min, company.salary_max,
            company.company_size, company.industry, company.job_url,
            company.notes, company.status, int(company.contacted),
            company.contact_name, company.contact_email, company.contact_phone
        ))
        return result.lastrowid

    def update_company(self, company: Company) -> bool:
        self.db.execute("""
            UPDATE companies SET
                name = ?, job_title = ?, job_type = ?, location = ?,
                work_mode = ?, salary_min = ?, salary_max = ?,
                company_size = ?, industry = ?, job_url = ?,
                notes = ?, status = ?, contacted = ?,
                contact_name = ?, contact_email = ?, contact_phone = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            company.name, company.job_title, company.job_type, company.location,
            company.work_mode, company.salary_min, company.salary_max,
            company.company_size, company.industry, company.job_url,
            company.notes, company.status, int(company.contacted),
            company.contact_name, company.contact_email, company.contact_phone,
            company.id
        ))
        return True

    def set_contacted(self, company_id: int, contacted: bool) -> bool:
        self.db.execute("""
            UPDATE companies
            SET contacted = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (int(contacted), company_id))
        return True

    def delete_company(self, company_id: int) -> bool:
        self.db.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        self.db.execute("DELETE FROM applications WHERE company_id = ?", (company_id,))
        return True

    def get_company(self, company_id: int) -> Optional[Company]:
        row = self.db.fetch_one("SELECT * FROM companies WHERE id = ?", (company_id,))
        return Company.from_row(row)

    def get_all_companies(self) -> List[Company]:
        rows = self.db.fetch_all("SELECT * FROM companies ORDER BY created_at DESC")
        return [Company.from_row(row) for row in rows]

    def get_companies_by_type(self, job_type: str) -> List[Company]:
        rows = self.db.fetch_all(
            "SELECT * FROM companies WHERE job_type = ? ORDER BY created_at DESC",
            (job_type,)
        )
        return [Company.from_row(row) for row in rows]

    def get_companies_by_status(self, status: str) -> List[Company]:
        rows = self.db.fetch_all(
            "SELECT * FROM companies WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        return [Company.from_row(row) for row in rows]

    def search_companies(self, query: str) -> List[Company]:
        search_term = f"%{query}%"
        rows = self.db.fetch_all("""
            SELECT * FROM companies WHERE
                name LIKE ? OR job_title LIKE ? OR job_type LIKE ? OR
                location LIKE ? OR industry LIKE ?
            ORDER BY created_at DESC
        """, (search_term, search_term, search_term, search_term, search_term))
        return [Company.from_row(row) for row in rows]

    def get_job_types(self) -> List[str]:
        rows = self.db.fetch_all(
            "SELECT DISTINCT job_type FROM companies WHERE job_type != '' ORDER BY job_type"
        )
        return [row['job_type'] for row in rows]

    def get_statuses(self) -> List[str]:
        return ["lista_deseos", "solicitado", "entrevista", "oferta", "rechazado"]

    def get_statistics(self) -> dict:
        total = self.db.fetch_one("SELECT COUNT(*) as count FROM companies")
        by_status = self.db.fetch_all("""
            SELECT status, COUNT(*) as count FROM companies GROUP BY status
        """)
        by_type = self.db.fetch_all("""
            SELECT job_type, COUNT(*) as count FROM companies
            WHERE job_type != '' GROUP BY job_type
        """)

        status_dict = {row['status']: row['count'] for row in by_status}
        type_dict = {row['job_type']: row['count'] for row in by_type}

        return {
            'total': total['count'] if total else 0,
            'by_status': status_dict,
            'by_type': type_dict
        }
