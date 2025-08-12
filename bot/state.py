import json

from asyncpg import Pool, create_pool

import bot.config as conf

from bot.repository.films import FilmsRepository
from bot.repository.user import UserRepository
from bot.repository.settings import SettingsRepository

class AppState:
    def __init__(self) -> None:
        self._db = None
        self._user_repo = None
        self._film_repo = None
        self._settings_repo = None

    async def _init_connection(self, conn):
        await conn.set_type_codec(
            "jsonb",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog",
        )

    async def startup(self) -> None:
        self._db = await create_pool(
            dsn=conf.DATABASE_DSN, init=self._init_connection
        )
        self._user_repo = UserRepository(self._db)
        self._film_repo = FilmsRepository(self._db)
        self._settings_repo = SettingsRepository(self._db)

    async def shutdown(self) -> None:
        if self._db:
            await self._db.close()
        if self._tg:
            await self._tg.stop_polling()

    @property
    def db(self) -> Pool:
        assert self._db
        return self._db
    
    @property
    def user_repo(self) -> UserRepository:
        assert self._user_repo
        return self._user_repo
    
    @property
    def film_repo(self) -> FilmsRepository:
        assert self._film_repo
        return self._film_repo

    @property
    def settings_repo(self) -> SettingsRepository:
        assert self._settings_repo
        return self._settings_repo

app_state = AppState()
