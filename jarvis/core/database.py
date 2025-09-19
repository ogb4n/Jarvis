from pymongo import MongoClient, IndexModel, TEXT
from typing import Optional
import logging

class DatabaseService:
    def __init__(self, mongodb_url: str, database_name: str = "jarvis"):
        self.client = MongoClient(mongodb_url)
        self.db = self.client[database_name]
        self._ensure_indexes()

    def _ensure_indexes(self):
        self.db.commands.create_indexes([
            IndexModel([("transcription", TEXT)]),
            IndexModel([("satellite_id", 1), ("created_at", -1)]),
            IndexModel([("session_id", 1)]),
            IndexModel([("command_type", 1), ("created_at", -1)])
        ])
        self.db.satellites.create_index([("name", 1)], unique=True)
        self.db.system_logs.create_indexes([
            IndexModel([("timestamp", -1)]),
            IndexModel([("level", 1), ("timestamp", -1)])
        ])
