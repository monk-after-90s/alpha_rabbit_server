from fastapi import APIRouter, Path, Request
from utilities import MarketType
from orm import KPatternGroup
from sqlalchemy import select
from orm import async_session

router = APIRouter()


@router.post("/{symbolType}/getAllPatternGroups")
async def get_all_pattern_groups(*,
                                 symbol_type: MarketType = Path(..., alias="symbolType"),
                                 request: Request):
    """获取全部形态组"""
    async with async_session() as session:
        # 执行查询并获取全部数据
        result = await session.execute(select(KPatternGroup))
        return result.scalars().all()
