# prediction_engine预测引擎，分为基础版和增强版。

1、 基础版Basic_Prediction(data,length=5)接受传入两个参数，第一个参数是所有历史行情数据，第二个参数是预测未来走势的长度。

1.1 先通过find_top_similar_patterns(self, top_n=5, corr_threshold=0.8)方法筛选出最匹配的top_n个形态，具体过程如下:
先通过相关系数阈值过滤掉大部分片段，如果剩下片段少于top_n个则全部纳入；如果多于top_n个再使用fastdtw算法进行匹配然后选出匹配度最高的前5个；

1.2 接下来通过extract_next_bars(self)方法找出筛选出的匹配度最高的片段后面的走势，然后对后续走势进行叠加，返回值为叠加后的K线走势和匹配度。

2、增强版Enhanced_Prediction(symbol_type,symbol,interval,datetime)，接受4个参数输入。

2.1 直接查数据库中往前推最近3个bar入选的形态， 对形态，去掉震荡类形态，然后比较多、空形态的数量，保留数量更多的形态类别；
如果形态类别相等则保留开始时间最近的一半形态。

2.2
fetch_pattern_data(self, patternId)
该方法可对所有形态进行历史行情回溯直接返回输入形态对未来8个bar预测的K线叠加走势（dataframe)

2.3通过方法prediction_method(self)去找步骤1中保留下来的形态对应步骤2中对未来预测的走势，得到多个预测走势后进行叠加。返回值为叠加后的走势以及
入选形态匹配度的平均值。



