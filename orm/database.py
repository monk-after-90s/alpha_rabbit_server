import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.engine import URL
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.sql.base import Executable
from sqlalchemy.sql import Select
from dotenv import load_dotenv

load_dotenv()


class SoftLogicDelAsyncSession(AsyncSession):
    """如果有字段is_delete作为逻辑删除的标识，忽视被逻辑删除的条目的异步会话"""

    async def execute(
            self,
            statement: Executable,
            *args,
            **kw: Any,
    ) -> Result[Any]:
        if isinstance(statement, Select) and hasattr(statement.c, 'is_delete'):
            statement = statement.filter_by(is_delete=0)
        return await super().execute(statement, *args, **kw)


# 0号数据库 创建异步SQLAlchemy引擎
engine0: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql",
               os.getenv("DB_USER"),
               os.getenv("DB_PASSWD"),
               os.getenv("DB_HOST"),
               os.getenv("DB_PORT"),
               os.getenv("DB0"),
               query={"charset": "utf8mb4", "init_command": "SET time_zone = '+08:00';"}),
    echo=True)
# 0号数据库的会话工厂
async_session_of_db0 = async_sessionmaker(engine0, expire_on_commit=False, class_=SoftLogicDelAsyncSession)
# 1号数据库 创建异步SQLAlchemy引擎
engine1: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql",
               os.getenv("DB_USER"),
               os.getenv("DB_PASSWD"),
               os.getenv("DB_HOST"),
               os.getenv("DB_PORT"),
               os.getenv("DB1"),
               query={"charset": "utf8mb4", "init_command": "SET time_zone = '+08:00';"}),
    echo=True)
# 1号数据库的会话工厂
async_session_of_db1 = async_sessionmaker(engine1, expire_on_commit=False, class_=SoftLogicDelAsyncSession)
