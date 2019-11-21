import pandas as pd
import ccxt
import datetime


def toDate(ts):
    ts = int(int(ts) / 1000)

    dateArray = datetime.datetime.utcfromtimestamp(ts)
    otherStyleTime = dateArray.strftime("%Y-%m-%d")
    return otherStyleTime


if __name__ == "__main__":
    binance = ccxt.binance()
    data = binance.fetch_ohlcv("BTC/USDT", "1d", params={"startTime": "1556640000000"})  # 从5月1日开始的数据
    kline = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', "close", "vol"])
    kline = kline.sort_values("date")

    # kline = ts.get_hist_data("510050", "2019-01-01")
    # kline = kline.sort_values("date")

    # 准备 df 对象
    df = pd.DataFrame()

    # 计算收盘价
    df["date"] = kline["date"].apply(toDate)
    df["close"] = kline["close"]
    df["change"] = df["close"] - df["close"].shift(1)  # 相比于前一日涨跌

    # 计算均线
    df["ma5"] = df["close"].rolling(window=5, center=False).mean()  # 计算5日均线
    df["ma20"] = df["close"].rolling(window=20, center=False).mean()  # 计算20日均线

    # 计算持仓
    df["pos"] = 0
    df["pos"][df["ma5"] >= df["ma20"]] = 1000  # 做多
    df["pos"][df["ma5"] < df["ma20"]] = -1000  # 做空
    df["pos"] = df["pos"].shift(1).fillna(0)

    # 计算盈亏
    df["pnl"] = df["change"] * df["pos"]  # 盈亏
    df["fee"] = 0
    df["fee"][df["pos"] != df["pos"].shift(1)] = df["close"] * 20000 * 0.0003  # 计算手续费
    df["netnpl"] = df["pnl"] - df["fee"]  # 净盈亏

    df = df.dropna()  # 抛弃NaN的数据

    # 盈亏汇总，绘制曲线
    df["cumpnl"] = df["netnpl"].cumsum()
    df["cumpnl"].plot()

    print(df)
