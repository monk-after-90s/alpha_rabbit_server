"""vnpy和币安标准的interval之间的转换"""


def bn_to_vnpy_interval(bn_interval: str):
    """币安标准的interval到vnpy标准"""
    if bn_interval == '1d':
        return 'd'
    if bn_interval == '1w':
        return 'w'
    return bn_interval
