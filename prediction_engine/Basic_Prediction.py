'''
用法示例：
result=Basic_Prediction(data,length=5)
result=result.extract_next_bars()
输入为历史行情数据以及用户选定的识别长度，返回值为两个，第一个值为一个dataframe，包含预测出的K线组合的高、低、收、开价格表，
第二个值为匹配度
'''
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from heapq import nsmallest
from operator import itemgetter

class Basic_Prediction:

    def __init__(self, data, length=5):

        self.ma_period = 10
        self.data=data.copy()
        # First, calculate moving average on self.data
        self.data['moving_average'] = self.data['close_price'].rolling(window=self.ma_period).mean()
        # Drop NaN values
        self.data = self.data.dropna()
        self.pattern = self.data.iloc[-length:].copy()
        self.pattern=self.pattern[['close_price','turnover','moving_average']]


    def create_pattern_series(self):
        pattern_dict = {}
        candles = self.data
        pattern_length = len(self.pattern)

        for i in range(len(candles) - pattern_length + 1):
            pattern = candles[['close_price', 'turnover', 'moving_average']].iloc[i: i + pattern_length]

            intersection = pattern.index.intersection(self.pattern.index)
            if intersection.empty:
                pattern = np.array(pattern)
                pattern_dict[i + pattern_length - 1] = pattern
        return pd.Series(pattern_dict)



    def normalize_series(self, dataframe):
        scaler = MinMaxScaler()
        dataframe_normalized = scaler.fit_transform(dataframe)


        return dataframe_normalized

    def find_top_similar_patterns(self, top_n=5, corr_threshold=0.8):
        pattern = self.pattern

        patterns_series = self.create_pattern_series()

        corr_coef_dict = {}
        for index, historical_pattern in patterns_series.iteritems():
            # Compute correlations for each feature and average them
            corr_close = np.corrcoef(pattern.iloc[:, 0].values.flatten(), historical_pattern[:, 0].flatten())[0, 1]
            corr_volume = np.corrcoef(pattern.iloc[:, 1].values.flatten(), historical_pattern[:, 1].flatten())[0, 1]
            corr_ma = np.corrcoef(pattern.iloc[:, 2].values.flatten(), historical_pattern[:, 2].flatten())[0, 1]
            avg_corr = np.mean([corr_close, corr_volume, corr_ma])

            if avg_corr >= corr_threshold:
                corr_coef_dict[index] = historical_pattern

        if len(corr_coef_dict) <= top_n:
            avg_corr_coef = np.mean(list(corr_coef_dict.values()))
            return list(corr_coef_dict.keys()), avg_corr_coef

        else:
            dtw_distances = {}
            for index, similar_pattern in corr_coef_dict.items():
                distance, _ = fastdtw(self.normalize_series(pattern), self.normalize_series(similar_pattern),
                                      dist=euclidean)
                dtw_distances[index] = distance

            top_similar_patterns = nsmallest(top_n, dtw_distances.items(), key=itemgetter(1))
            top_indices_and_patterns = [index for index, _ in top_similar_patterns]
            corr_list = [corr_coef_dict[i] for i in top_indices_and_patterns]

            return top_indices_and_patterns, np.mean(corr_list)

    def extract_next_bars(self):

        next_pattern_list = []
        candles = self.data
        index_list = self.find_top_similar_patterns()[0]
        next_bars = len(self.pattern)
        if len(index_list) != 0:
            for index in index_list:
                if index + 1 + next_bars <= len(candles):
                    result = candles.iloc[index + 1: index + 1 + next_bars]
                    result = result[['high_price', 'low_price', 'close_price', 'open_price']]
                    result = result / (result['open_price'].iloc[0])

                    next_pattern_list.append(result)

            if len(next_pattern_list)!=0:
                total_array = np.mean([df.values for df in next_pattern_list], axis=0)

                # 将结果转换回DataFrame
                sum_df = pd.DataFrame(total_array, columns=next_pattern_list[0].columns)
                sum_df = sum_df * self.pattern['close_price'].iloc[-1]

                return sum_df,self.find_top_similar_patterns()[1]
            else:
                return None

        else:
            return None
