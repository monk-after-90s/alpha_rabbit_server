from fastapi import APIRouter, Path, Request
from utilities import MarketType
from orm import KPatternGroup
from sqlalchemy import select
from orm import async_session
from sqlalchemy.orm import selectinload

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


@router.post("/{symbolType}/getGrpPatterns")
async def get_grp_patterns(request: Request):
    """获取指定形态组的形态"""
    async with async_session() as session:
        # 形态组id
        pattern_grp_id: int = (await request.json()).get('patternGrpId')
        # 形态组
        stmt = select(KPatternGroup).options(selectinload(KPatternGroup.k_patterns)).where(
            KPatternGroup.id == pattern_grp_id)
        result = await session.execute(stmt)
        pattern_grp = result.scalars().first()
        return {
            "id": pattern_grp.id,
            "name": pattern_grp.name,
            "patterns": pattern_grp.k_patterns
        }
