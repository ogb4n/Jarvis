from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class CommandType(str, Enum):
    DOMOTIQUE = "domotique"
    LLM = "llm"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class Command:
    satellite_id: str
    session_id: str
    transcription: Optional[str] = None
    command_type: CommandType = CommandType.UNKNOWN
    response_text: Optional[str] = None
    success: bool = False
    processing_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None
    _id: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self._id is None:
            data.pop('_id', None)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        return cls(**data)
