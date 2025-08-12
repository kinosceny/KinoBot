import logging
from datetime import datetime

from asyncpg import Pool
from pydantic import BaseModel

from bot.repository.helpers import build_model_sql

logger = logging.getLogger(__name__)


class User(BaseModel):
    id: int | None = None
    telegram_id: int
    films: list[int]
    created_timestamp: datetime | None = None


class UserRepository:
    def __init__(self, db: Pool):
        self._db = db

    async def get_by_id(self, user_id: int) -> User | None:
        sql = """
            SELECT *
            FROM "users"
            WHERE "id" = $1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, user_id)

        if not row:
            return

        return User(**dict(row))

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        sql = """
            SELECT *
            FROM "users"
            WHERE "telegram_id" = $1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, telegram_id)

        if not row:
            return

        return User(**dict(row))

    async def create(self, user: User) -> User | None:
        modelSQL = build_model_sql(user, True)
        sql = f"""
            INSERT INTO "users"
            ({modelSQL.field_names})
            VALUES ({modelSQL.placeholders})
            ON CONFLICT ("id")
            DO NOTHING
            RETURNING *
        """

        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, *modelSQL.values)

        if not row:
            return None

        return User(**dict(row))
    
    async def update_by_id(self, id, key, value) -> bool | None:
        sql = f"""
            UPDATE "users"
            SET "{key}" = $1
            WHERE "id" = $2
            RETURNING 1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, value, id)

        return row is not None