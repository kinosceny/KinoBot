import logging

from asyncpg import Pool
from typing import List
from pydantic import BaseModel

from bot.repository.helpers import build_model_sql

logger = logging.getLogger(__name__)


class Film(BaseModel):
    id: int | None = None
    film_id: int
    path_to_video: str
    icon: str
    video_name: str
    film_name: str
    text: str
    link: str
    link_found: str
    link_text: str


class FilmsRepository:
    def __init__(self, db: Pool):
        self._db = db

    async def create(self, film: Film) -> Film | None:
        modelSQL = build_model_sql(film, True)
        sql = f"""
            INSERT INTO "films"
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

        return Film(**dict(row))

    async def get_all(self) -> List[Film] | None:
        sql = """
            SELECT *
            FROM "films"
        """
        async with self._db.acquire() as c:
            rows = await c.fetch(sql)

        if not rows:
            return None

        return [Film(**dict(row)) for row in rows]
    
    async def find_by_id(self, id: int) -> Film:
        sql = """
            SELECT *
            FROM "films"
            WHERE "id" = $1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, id)

        if not row:
            return None

        return Film(**dict(row))
    
    async def find_by_film_id(self, film_id: int) -> Film:
        sql = """
            SELECT *
            FROM "films"
            WHERE "film_id" = $1
        """
        async with self._db.acquire() as c:
            row = await c.fetchrow(sql, film_id)

        if not row:
            return None

        return Film(**dict(row))
    
    async def delete_by_film_id(self, film_id: int) -> bool:
        sql = """
            DELETE
            FROM films
            WHERE film_id = $1
            RETURNING film_id
        """
        async with self._db.acquire() as c:
            val = await c.fetchval(sql, film_id)

        return val is not None

