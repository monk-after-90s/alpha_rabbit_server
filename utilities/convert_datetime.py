from datetime import datetime
from pytz import timezone

beijing_tz = timezone('Asia/Shanghai')


def convert_to_sh(dt: datetime) -> datetime:
    """
    将datetime转成上海时区
    dt带时区信息的话根据时区转，否则直接加上上海时区
    """
    dt_beijing = dt.astimezone(beijing_tz)
    return dt_beijing
