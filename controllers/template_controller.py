from typing import List, Optional
from models.template import Template
from utils.database import get_db

class TemplateController:
    def __init__(self):
        self.db = get_db()

    def add_template(self, template: Template) -> int:
        result = self.db.execute("""
            INSERT INTO templates (name, content, style)
            VALUES (?, ?, ?)
        """, (template.name, template.content, template.style))
        return result.lastrowid

    def update_template(self, template: Template) -> bool:
        self.db.execute("""
            UPDATE templates SET name = ?, content = ?, style = ?
            WHERE id = ?
        """, (template.name, template.content, template.style, template.id))
        return True

    def delete_template(self, template_id: int) -> bool:
        self.db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        return True

    def get_template(self, template_id: int) -> Optional[Template]:
        row = self.db.fetch_one("SELECT * FROM templates WHERE id = ?", (template_id,))
        return Template.from_row(row)

    def get_all_templates(self) -> List[Template]:
        rows = self.db.fetch_all("SELECT * FROM templates ORDER BY created_at DESC")
        return [Template.from_row(row) for row in rows]


class PromptHistoryController:
    def __init__(self):
        self.db = get_db()

    def add_prompt(self, prompt_text: str, company_name: str = "") -> int:
        result = self.db.execute("""
            INSERT INTO prompt_history (prompt_text, company_name)
            VALUES (?, ?)
        """, (prompt_text, company_name))
        return result.lastrowid

    def get_recent_prompts(self, limit: int = 10) -> List[dict]:
        rows = self.db.fetch_all("""
            SELECT * FROM prompt_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in rows]

    def delete_prompt(self, prompt_id: int) -> bool:
        self.db.execute("DELETE FROM prompt_history WHERE id = ?", (prompt_id,))
        return True
