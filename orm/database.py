from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from setting import DB_HOST, DB_PORT, DB_USER, DB_PASSWD, DB
from sqlalchemy.engine import URL

# 创建异步SQLAlchemy引擎
engine: AsyncEngine = create_async_engine(URL.create("mysql+aiomysql", DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB),
                                          echo=True)