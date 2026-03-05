"""Task data model used to represent task entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Dataclass representing a single task with its metadata.

    Attributes:
        id: Unique identifier of the task.
        title: Short title describing the task.
        description: Optional longer description.
        is_active: Whether the task is still active (not done).
        created_at: Timestamp when the task was created.
        updated_at: Timestamp of the last update, if any.
    """
    id: int
    title: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Serialize the task to a dictionary suitable for JSON responses."""
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
