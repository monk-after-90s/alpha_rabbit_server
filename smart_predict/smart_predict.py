from fastapi import APIRouter, Path, Request
from utilities import MarketType

router = APIRouter()


@router.post("/{symbolType}/smartPred")
async def smart_pred(*,
                     symbol_type: MarketType = Path(..., alias="symbolType"),
                     request: Request):
    return await request.json()
