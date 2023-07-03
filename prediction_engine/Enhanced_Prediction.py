'''
使用方法如下：method=Enhanced_Prediction(symbol_type,symbol,interval,datetime)
result=method.prediction_method()
该方法返回两个值，第一个值为一个列表，列表里面有一个或者最多三个未来8天的走势，每个走势由一个dataframe记录,包含开、高、低、收4个序列，第二个值为匹配度
'''
from sqlalchemy import create_engine, text
import pandas as pd


class Enhanced_Prediction:
    def __init__(self, symbol_type, symbol, interval, datetime):
        self.user = "szhb"
        self.password = "Vlink168168"
        self.host1 = "rm-wz93wz2ew5j3di360-l3.mysql.rds.aliyuncs.com"
        self.host2 = "rm-wz93wz2ew5j3di360-l3.mysql.rds.aliyuncs.com"
        self.database1 = "quant"
        self.database2 = "alpha_rabit_dev"
        self.symbol_type = symbol_type
        self.symbol = symbol
        self.interval = interval
        self.datetime = datetime

    def get_data1(self):
        if self.symbol_type == 'spot':
            symbol = self.symbol.replace("/", "").lower()
        elif self.symbol_type == 'futures':
            symbol = self.symbol.replace("/", "").upper()

        interval = self.interval

        engine = create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.host1}/{self.database1}')

        query = text(f"SELECT * FROM dbbardata WHERE symbol=:symbol AND `interval`=:interval")
        with engine.begin() as connection:
            df = pd.read_sql_query(query, connection, params={'symbol': symbol, 'interval': interval})
            df['datetime'] = pd.to_datetime(df['datetime'])
        return df

    def get_data2(self):
        symbol_type = self.symbol_type
        symbol = self.symbol
        interval = self.interval

        engine = create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.host2}/{self.database2}')

        query = text(
            f"SELECT * FROM pattern_recognize_record WHERE symbol_type=:symbol_type AND symbol=:symbol AND `interval`=:interval")
        with engine.begin() as connection:
            df = pd.read_sql_query(query, connection,
                                   params={'symbol_type': symbol_type, 'symbol': symbol, 'interval': interval})

        return df

    def fetch_filtered_data(self):
        # 获取两个数据集
        data1 = self.get_data1()
        data2 = self.get_data2()
        data2['patternStart'] = pd.to_datetime(data2['patternStart'])
        data2['patternEnd'] = pd.to_datetime(data2['patternEnd'])

        # 在data1中找到self.datetime的位置，然后向前推3个索引
        target_index = data1[data1['datetime'] == self.datetime].index[0]
        start_index = target_index - 3 if target_index >= 3 else 0
        date_range = data1.iloc[start_index:target_index + 1]['datetime'].tolist()

        # 在data2中筛选出patternEnd落在这个范围内的行
        filtered_data2 = data2[data2['patternEnd'].isin(date_range)]

        return filtered_data2

    # 找出历史上特定形态的叠加走势（归一化）
    def fetch_pattern_data(self, patternId):
        # 获取两个数据集
        data1 = self.get_data1()
        data2 = self.get_data2()
        data2['patternStart'] = pd.to_datetime(data2['patternStart'])
        data2['patternEnd'] = pd.to_datetime(data2['patternEnd'])

        # 在data2中找到patternId等于输入参数的所有行
        target_rows = data2[data2['patternId'] == patternId]

        if len(target_rows) == 0:
            return None

        # 初始化一个空列表来存储所有得到的DataFrame
        dataframes = []

        # 对于每一个筛选出来的patternEnd值
        for patternEnd in target_rows['patternEnd']:
            # 在data1中找到patternEnd对应的索引
            target_index = data1[data1['datetime'] == patternEnd].index[0]

            # 判断是否有足够的索引进行切片
            if target_index + 8 < len(data1):
                # 如果有，进行切片并取出需要的列
                df = data1.iloc[target_index:target_index + 8][['open_price', 'close_price', 'high_price', 'low_price']]
                df = df / df['open_price'].iloc[0]
                # 重新索引，使索引从0开始
                df = df.reset_index(drop=True)
                dataframes.append(df)

        if len(dataframes) == 0:
            return None

            # 计算所有归一化后的DataFrame的平均值
        average_trend = pd.concat(dataframes).groupby(level=0).mean()

        return average_trend

    # 直接返回该次预测值
    def prediction_method(self):
        # 获取第二个数据集
        filtered_data2 = self.get_data2()

        # 检查长度，如果为0，直接返回None
        if len(filtered_data2) == 0:
            return None

        # 删除patternId为5或15的行
        filtered_data2 = filtered_data2[~filtered_data2['patternId'].isin([5, 15])]

        # 再次检查长度，如果为0，直接返回None
        if len(filtered_data2) == 0:
            return None

        # 如果长度为1，找出patternId的值
        if len(filtered_data2) == 1:
            patternId = filtered_data2['patternId'].iloc[0]

            # 使用找到的patternId调用fetch_pattern_data方法并返回结果
            return self.fetch_pattern_data(patternId)

        elif len(filtered_data2) > 1:
            filtered_data2['new_column'] = filtered_data2['patternId'].apply(
                lambda x: 1 if x in (2, 3, 7, 9, 16, 17, 18, 19) else 0)

            # 统计新列中1和0的数量
            count_1 = filtered_data2['new_column'].sum()
            count_0 = len(filtered_data2) - count_1

            # 如果1的数量大于0的数量，删除等于0的行，反之删除等于1的行
            if count_1 > count_0:
                filtered_data2 = filtered_data2[filtered_data2['new_column'] == 1]
            elif count_0 > count_1:
                filtered_data2 = filtered_data2[filtered_data2['new_column'] == 0]
            else:
                # 如果数量相等，删除patternStart值较小的一半行
                filtered_data2 = filtered_data2.sort_values('patternStart')
                filtered_data2 = filtered_data2[int(len(filtered_data2) / 2):]
            # 计算平均匹配度
            corre = filtered_data2['matchScore'].mean()

            # 获取patternId的唯一值
            unique_pattern_ids = filtered_data2['patternId'].unique()

            # 对每个唯一的patternId调用fetch_pattern_data方法
            dataframes = [self.fetch_pattern_data(id) for id in unique_pattern_ids]

            # 如果1的数量等于0的数量，对所有dataframe进行平均
            if count_1 == count_0:
                dataframes = [pd.concat(dataframes).groupby(level=0).mean()]

            # 获取第一个数据集
        data1 = self.get_data1()

        # 获取self.datetime对应的close_price
        close_price = data1[data1['datetime'] == self.datetime]['close_price'].iloc[0]

        # 对每个dataframe的值进行还原
        dataframes = [df * close_price for df in dataframes]

        # 只返回前三个dataframes
        return dataframes[:3],corre


