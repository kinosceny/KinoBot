import logging
from datetime import datetime

from asyncpg import Pool
from pydantic import BaseModel

from bot.repository.helpers import build_model_sql

logger = logging.getLogger(__name__)


class Settings(BaseModel):
    id: int | None = None
    start_message: str
    code_message: str
    after_link: str
    not_found_code_message: str
    is_working: bool


class SettingsRepository:
    def __init__(self, db: Pool):
        self._db = db

    async def get_all(self) -> Settings | None:
        sql = """
            SELECT *
            FROM "bot_settings"
            WHERE "id" = 1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql)

        if not row:
            return

        return Settings(**dict(row))
    
    async def update(self, key, value) -> bool | None:
        sql = f"""
            UPDATE "bot_settings"
            SET "{key}" = $1
            WHERE "id" = 1
            RETURNING 1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, value)

        return row is not None
