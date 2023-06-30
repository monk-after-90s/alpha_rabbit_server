from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from setting import DB_HOST, DB_PORT, DB_USER, DB_PASSWD, DB
from sqlalchemy.engine import URL
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql.base import Executable
from sqlalchemy.sql import Select

# 创建异步SQLAlchemy引擎
engine: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql", DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB,
               query={"charset": "utf8mb4", "init_command": "SET time_zone = '+08:00';"}),
    echo=True)


class LogicDelAsyncSession(AsyncSession):
    """忽视被逻辑删除的条目的异步会话"""

    async def execute(
            self,
            statement: Executable,
            *args,
            **kw: Any,
    ) -> Result[Any]:
        if isinstance(statement, Select):
            statement = statement.filter_by(is_delete=0)
        return await super().execute(statement, *args, **kw)


async_session = async_sessionmaker(engine, expire_on_commit=False, class_=LogicDelAsyncSession)
