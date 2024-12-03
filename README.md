# init

```shell
/usr/bin/python3.8 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. market_history.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. market_history.proto
```

# build

```shell
pip install --upgrade setuptools

rm -rf marketrpc.egg-info dist build python_marketrpc.egg-info
python setup.py sdist bdist_wheel

pip install ./dist/marketrpc-0.0.1-py3-none-any.whl
```

# Tips

**SDK仅允许内网访问使用**

**A股数据仅有K线，无成交流，订单簿**

# K线数据

> 必要参数必须填上其他非必要可不填，默认为币安数据，A股数据需要根据请求参数指定字段

| 参数                    | 类型   | 关键参数 | 备注                                                                                                       |
| --------------------- | ---- | ---- | -------------------------------------------------------------------------------------------------------- |
| schema                | str  | ×    | 模式名，币安：BINANCE，A股：ASTOCK，(default:BINANCE)                                                               |
| type                  | str  | ×    | 数据类型，(default: KLINE)                                                                                    |
| exchange              | str  | ×    | 交易所名称，币安：BINANCE，A股票：1, (default:binance)                                                                |
| account_type          | str  | √    | 账户类型，币安：future/spot，A股上证：1，A股票深证：2                                                                       |
| symbol                | str  | √    | 交易对，加密货币支持列表(adausdt, bnbusdt, btcusdt, dogeusdt, ethusdt, solusdt, xrpusdt)，股票个股交易对(交易代码 000001 600519) |
| kline_interval_second | str  | ×    | K线时间间隔，币安1s，A股60s，(default:1)                                                                            |
| start_time            | str  | √    | 开始时间戳                                                                                                    |
| end_time              | str  | √    | 结束时间戳                                                                                                    |
| start_id              | str  | ×    | 开始ID(default:0)                                                                                          |
| end_id                | str  | ×    | 结束ID(default:0)                                                                                          |
| limit                 | str  | ×    | 数据限制数量(default:10000)                                                                                    |
| is_asc                | str  | ×    | 是否升序排列(default:True)                                                                                     |
| is_gzip               | str  | ×    | 是否使用gzip压缩(default:False)                                                                                |
| debug                 | bool | ×    | (default:False)                                                                                          |

## binance btcusdt future

```python
from marketrpc.rpcUtils import datetime_to_millis, market_kline

if __name__ == '__main__':
    start_time = datetime_to_millis("2024-12-02 10:00:00")
    end_time=datetime_to_millis("2024-12-02 10:59:59")
   
    # 查询BTCUSDT K线数据 start_time ~ end_time的前5条数据
    result = market_kline(
        account_type='future',
        symbol="btcusdt",
        kline_interval_second=1,
        start_time=start_time,
        end_time=end_time,
        limit=5
    )
    print(f"获取 {len(result[0])} 条数据")
    for item in reversed(result[0]):
        print(f"{item}")
```

## astock 贵州茅台

```python
from marketrpc.rpcUtils import datetime_to_millis, market_kline

if __name__ == '__main__':
    start_time = datetime_to_millis("2024-12-02 10:00:00")
    end_time = datetime_to_millis("2024-12-02 10:59:59")
   
    # 查询BTCUSDT K线数据
    result = market_kline(
        schema="astock",
        exchange="1",
        account_type="1",
        symbol="600519",
        kline_interval_second=60,
        start_time=start_time,
        end_time=end_time,
        limit=5
    )
    print(f"获取 {len(result[0])} 条数据")
    for item in reversed(result[0]):
        print(f"{item}")
```

# 成交流

## binance btcusdt future

```python
from marketrpc.rpcUtils import datetime_to_millis, market_aggtrade

if __name__ == '__main__':
    start_time = datetime_to_millis("2024-12-02 10:00:00")
    end_time = datetime_to_millis("2024-12-02 10:59:59")

    # 查询市场成交流数据
    result = market_aggtrade(
        exchange="binance",
        account_type="future",
        symbol="btcusdt",
        start_time=start_time,
        end_time=end_time,
        limit = 5
    )
    print(f"获取 {len(result[0])} 条数据")
    for item in (result[0]):
        print(f"{item}")
```

# 市场订单簿数据

## binance btcusdt future

```python
from marketrpc.rpcUtils import datetime_to_millis, market_aggtrade

if __name__ == '__main__':
    start_time = datetime_to_millis("2024-12-02 10:00:00")
    end_time = datetime_to_millis("2024-12-02 10:59:59")

    # 查询市场订单簿数据
    result = market_orderbook(
        exchange="binance",
        account_type="future",
        symbol="btcusdt",
        start_time=start_time,
        end_time=end_time,
        limit = 5
    )
    print(f"获取 {len(result[0])} 条数据")
    for item in (result[0]):
        print(f"{item}")
```