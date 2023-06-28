from fastapi import APIRouter, Path, Request
from utilities import MarketType

router = APIRouter()


@router.post("/{symbolType}/getAllPatternGroups")
async def get_all_pattern_groups(*,
                                 symbol_type: MarketType = Path(..., alias="symbolType"),
                                 request: Request):
    """获取全部形态组"""
    return [
        {
            "id": 0,
            "name": "string"
        }
    ]
