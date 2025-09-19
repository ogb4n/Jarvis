from jarvis.core.database import DatabaseService
from jarvis.models.command import Command
from typing import List, Optional
from bson import ObjectId

class CommandService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service.db

    def create_command(self, command: Command) -> str:
        result = self.db.commands.insert_one(command.to_dict())
        return str(result.inserted_id)

    def get_command(self, command_id: str) -> Optional[Command]:
        doc = self.db.commands.find_one({"_id": ObjectId(command_id)})
        return Command.from_dict(doc) if doc else None

    def search_commands(self, query: str, limit: int = 20) -> List[Command]:
        cursor = self.db.commands.find({"$text": {"$search": query}}).sort("created_at", -1).limit(limit)
        return [Command.from_dict(doc) for doc in cursor]

    def get_recent_commands(self, satellite_id: str, limit: int = 10) -> List[Command]:
        cursor = self.db.commands.find({"satellite_id": satellite_id}).sort("created_at", -1).limit(limit)
        return [Command.from_dict(doc) for doc in cursor]
