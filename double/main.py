import ccxt
import datetime
import pandas as pd
import matplotlib.pyplot as plt


def toDate(ts):
    ts = int(int(ts) / 1000) + (60 * 60 * 8)
    dateArray = datetime.datetime.utcfromtimestamp(ts)
    otherStyleTime = dateArray.strftime("%H:%M")
    return otherStyleTime


if __name__ == '__main__':
    ma1 = 5
    ma2 = 20
    series1 = "ma{}".format(ma1)
    series2 = "ma{}".format(ma2)

    # 总资产
    Money = 10000

    # 查询k线
    ex = ccxt.huobipro()
    kline_1m = ex.fetch_ohlcv("EOS/USDT", "1m", limit=200)

    # 准备数据，日期升序排列
    df = pd.DataFrame(kline_1m, columns=['date', 'open', 'high', 'low', "close", "vol"])
    df['date'] = df['date'].apply(toDate)
    df = df.set_index('date')
    df = df.sort_values("date")

    # 计算均线
    df[series1] = df["close"].rolling(window=ma1, center=False).mean()  # 计算5日均线
    df[series2] = df["close"].rolling(window=ma2, center=False).mean()  # 计算20日均线

    # 计算持仓
    df["pos"] = 0
    df["pos"][df[series1] >= df[series2]] = 1000  # 做多
    df["pos"][df[series1] < df[series2]] = -1000  # 做空
    df["pos"] = df["pos"].shift(1).fillna(0)

    # 计算变动
    df["change"] = (df["close"] - df["close"].shift(1)) / df["close"].shift(1)  # 相比于前一次涨跌百分比

    # 计算盈亏
    df["pnl"] = df["change"] * df["pos"]  # 盈亏
    df["fee"] = 0
    df["fee"][df["pos"] != df["pos"].shift(1)] = 1000 * 0.0003  # 计算手续费
    df["netnpl"] = df["pnl"] - df["fee"]  # 净盈亏

    # 总盈亏
    df["cumpnl"] = df["netnpl"].cumsum()

    df = df.dropna()

    # print(df.to_csv('a.csv'))
    print(df)

    # 画线
    df[series1].plot.line(label=series1, color="red")
    df[series2].plot.line(label=series2, color="blue")
    # df['cumpnl'].plot.line(label='cumpnl', color="green")

    plt.legend([series1, series2, 'cumpnl'])
    plt.show()
