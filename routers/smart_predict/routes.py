import asyncio
import json
import pandas as pd
from pandas import DataFrame, Timestamp
from prediction_engine import Basic_Prediction, Enhanced_Prediction
from fastapi import APIRouter, Path, Request
from utilities import MarketType, bn_to_vnpy_interval
from concurrent.futures import ProcessPoolExecutor
from orm import async_session_of_db1, Dbbardata
from sqlalchemy import select
from utilities import symbol_united2vnpy, INTERVAL_SECS_MAP, convert_to_utc
from datetime import timedelta

router = APIRouter()

executor = ProcessPoolExecutor()


@router.post("/{symbolType}/smartPred")
async def smart_pred(*,
                     symbol_type: MarketType = Path(..., alias="symbolType"),
                     request: Request):
    symbol_type = str(symbol_type.value)
    # 处理post参数
    print(f"{await request.body()=}")
    params = await request.json()

    stmt = select(Dbbardata)
    # 参数搜集
    exchange = 'BINANCE'
    if 'exchange' in params:
        exchange = params['exchange']
    # 转换symbol
    symbol = params['symbol']
    vnpy_symbol = await symbol_united2vnpy(exchange, symbol_type, symbol)
    stmt = stmt.where(Dbbardata.symbol == str(vnpy_symbol))
    stmt = stmt.where(Dbbardata.exchange == exchange)
    # 转换interval
    kInterval = params['kInterval']
    vnpy_interval = bn_to_vnpy_interval(kInterval)
    stmt = stmt.where(Dbbardata.interval == str(vnpy_interval))

    isPro = False
    if 'isPro' in params:
        isPro = params['isPro']

    kNum = 0
    if 'kNum' in params:
        kNum = params['kNum']
    async with async_session_of_db1() as session:
        # 计算
        if not isPro:
            # 数据获取
            result = (await session.execute(stmt)).scalars().all()
            bar_df = pd.DataFrame(
                map(lambda bar: {col: getattr(bar, col) for col in stmt.columns.keys()}, result),
                columns=stmt.columns.keys()
            )

            prediction = await asyncio.get_running_loop().run_in_executor(
                executor,
                Basic_Prediction(bar_df, length=kNum).extract_next_bars)

            if result:
                last_date_time = result[-1].datetime
        else:
            # 查询最后的柱子datetime
            newest_datetime = (
                await session.execute(
                    select(Dbbardata.datetime).
                    where(Dbbardata.symbol == str(vnpy_symbol),
                          Dbbardata.exchange == str(exchange),
                          Dbbardata.interval == str(vnpy_interval)).
                    order_by(Dbbardata.id.desc()).limit(1)
                )
            ).scalar()

            if newest_datetime is None:
                return {
                    "code": -1,
                    "msg": "没有K线记录"
                }
            else:
                last_date_time = newest_datetime

            prediction = await asyncio.get_running_loop().run_in_executor(
                executor,
                Enhanced_Prediction(
                    symbol_type,
                    symbol,
                    kInterval,
                    Timestamp(newest_datetime.replace(tzinfo=None))
                ).prediction_method)

        data = []
        match_score = 0
        if prediction is None:
            ...
        else:
            pred_bars, match_score = prediction[0], prediction[1]
            # 分isPro处理
            if not isPro:
                pred_bars: DataFrame
                data.append(json.loads(pred_bars.to_json(orient='records')))
            else:
                data = list(map(lambda pred_bars_df: json.loads(pred_bars_df.to_json(orient='records')), pred_bars))
                pass
        # 添加时间字段
        for k_lines in data:
            for k_line in k_lines:
                last_date_time += timedelta(seconds=INTERVAL_SECS_MAP[vnpy_interval])
                k_line['datetime'] = last_date_time
        # ToDo 数据库缓存
        return {
            "symbolType": symbol_type,
            "symbol": symbol,
            "exchange": exchange,
            "kInterval": kInterval,
            "isPro": isPro,
            "kNum": kNum,
            "match_score": match_score,
            "data": data
        }
