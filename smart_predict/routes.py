from fastapi import APIRouter, Path, Request
from utilities import MarketType

router = APIRouter()


@router.post("/{symbolType}/smartPred")
async def smart_pred(*,
                     symbol_type: MarketType = Path(..., alias="symbolType"),
                     request: Request):
    return {
        "symbol": "string",
        "symbolType": "spot",
        "kInterval": "1d",
        "kNum": 0,
        "accuracy": 0,
        "data": [
            {
                "datetime": "2019-08-24T14:15:22Z",
                "open": 0,
                "high": 0,
                "low": 0,
                "close": 0
            }
        ]
    }
