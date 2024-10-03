from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel

DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class Event(BaseModel):
    id: int
    description: Optional[str] = None
    time: datetime

    def __post_init__(self):
        pass

    def convert_to_mongodb_record(self) -> Dict[str, Any]:
        return {**self.model_dump(), "_id": self.id}

    def format_time(self, pattern=None) -> Dict[str, Any]:
        if not pattern:
            pattern = DEFAULT_DATETIME_FORMAT

        new_time = self.time.strftime(format=pattern)

        attributes = {"id": self.id, "description": self.description, "time": new_time}

        return attributes
