from sqlalchemy import TypeDecorator, TIMESTAMP
from datetime import datetime
from utilities import convert_to_utc


class TimestampWithTimezone(TypeDecorator):
    """可以将MySQL表TIMESTAMP字段反序列化为带有时区信息的datetime的SQLAlchemy字段"""
    impl = TIMESTAMP

    def process_result_value(self, value: datetime, dialect):
        if value is not None:
            # 将结果值转换为带时区的 datetime 对象
            value = convert_to_utc(value)
        return value