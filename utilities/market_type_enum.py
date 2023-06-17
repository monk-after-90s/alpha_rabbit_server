from enum import Enum


class MarketType(Enum):
    """市场类型"""
    spot = "spot"
    swap = "swap"
    future = "future"
