from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Template:
    id: Optional[int] = None
    name: str = ""
    content: str = ""
    style: str = "modern"
    created_at: Optional[datetime] = None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'style': self.style,
            'created_at': self.created_at
        }

    @classmethod
    def from_row(cls, row):
        if row is None:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            content=row['content'],
            style=row['style'],
            created_at=row['created_at']
        )
