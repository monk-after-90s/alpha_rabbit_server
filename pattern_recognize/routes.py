import datetime

from fastapi import APIRouter, Path, Request
from utilities import MarketType
from orm import KPatternGroup, PatternRecognizeRecord
from sqlalchemy import select
from orm import async_session
from sqlalchemy.orm import selectinload
from dateutil.parser import parse

router = APIRouter()


@router.post("/{symbolType}/getAllPatternGroups")
async def get_all_pattern_groups():
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


@router.post("/{symbolType}/recognizePattern")
async def recognize_pattern(*,
                            symbol_type: MarketType = Path(..., alias="symbolType"),
                            request: Request):
    """形态识别"""
    async with async_session() as session:
        # 市场类型
        stmt = select(PatternRecognizeRecord).where(
            PatternRecognizeRecord.symbol_type == str(symbol_type.value)).order_by(PatternRecognizeRecord.id)
        # 分页
        page: int = 1
        per_page: int = 10
        # 处理post参数
        recognize_param = await request.json()
        # 参数搜集
        ## 普通参数
        if 'page' in recognize_param:
            page = recognize_param['page']
        if 'per_page' in recognize_param:
            per_page = recognize_param['per_page']
        if 'exchange' in recognize_param:
            stmt = stmt.where(PatternRecognizeRecord.exchange == str(recognize_param['exchange']))
        if 'symbol' in recognize_param:
            stmt = stmt.where(PatternRecognizeRecord.symbol == str(recognize_param['symbol']))
        if 'kInterval' in recognize_param:
            stmt = stmt.where(PatternRecognizeRecord.kInterval == str(recognize_param['kInterval']))
        if 'start' in recognize_param:
            stmt = stmt.where(PatternRecognizeRecord.patternEnd >= parse(recognize_param['start']))
        if 'end' in recognize_param:
            stmt = stmt.where(PatternRecognizeRecord.patternEnd <= parse(recognize_param['end']))
        ## patternIds
        if 'patternIds' in recognize_param:
            pattern_ids = recognize_param['patternIds']

            stmt = stmt.where(PatternRecognizeRecord.id.in_(pattern_ids))

        # 计算需要跳过的项的数量
        skip = (page - 1) * per_page
        stmt = stmt.offset(skip).limit(per_page)
        # 执行语句
        result = await session.execute(stmt)
        pattern_recognize_records = result.scalars().all()

        # 统计
        start = datetime.datetime(3000, 1, 1)
        end = datetime.datetime(1970, 1, 1)
        for pattern_recognize_record in pattern_recognize_records:
            if pattern_recognize_record.patternEnd < start:
                start = pattern_recognize_record.patternEnd
            if pattern_recognize_record.patternEnd > end:
                end = pattern_recognize_record.patternEnd
        return {
            'start': start,
            'end': end,
            'len': len(pattern_recognize_records),
            'data': pattern_recognize_records,
            'pagination': {
                "current_page": page,
                "per_page": per_page,
            }
        }
