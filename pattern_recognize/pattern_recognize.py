from fastapi import APIRouter, Path, Request
from utilities import MarketType
from orm import Session, KPatternGroup
from sqlalchemy import select
from loguru import logger

router = APIRouter()


@router.post("/{symbolType}/getAllPatternGroups")
async def get_all_pattern_groups(*,
                                 symbol_type: MarketType = Path(..., alias="symbolType"),
                                 request: Request):
    """获取全部形态组"""
    async with Session() as session:
        # 执行查询并获取全部数据
        sql = select(KPatternGroup)
        result = await session.execute(sql)
    return result.scalars().all()
