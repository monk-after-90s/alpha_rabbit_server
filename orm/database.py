from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from setting import DB_HOST, DB_PORT, DB_USER, DB_PASSWD, DB
from sqlalchemy.engine import URL

# 创建异步SQLAlchemy引擎
engine: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql", DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB,
               query={"charset": "utf8mb4", "init_command": "SET time_zone = '+00:00';"}),
    echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
