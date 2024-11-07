import logging

from marketrpc.rpcUtils import datetime_to_millis, market_kline
from marketrpc import *

logging.basicConfig(level=logging.INFO,format="[%(name)s][%(asctime)s][%(filename)s:%(lineno)d]\t%(levelname)s\t%(message)s",)

if __name__ == '__main__':
    start_time = datetime_to_millis("2024-11-06 12:00:00")
    end_time=datetime_to_millis("2024-11-06 12:05:00")
    logging.info(f"start_time: {start_time}, start_timetype: {type(start_time)}, end_time: {end_time}, end_timetype: {type(end_time)}")

    # 查询市场K线数据
    result = market_kline(
        exchange="BINANCE",
        account_type="future",
        symbol="BTCUSDT",
        kline_interval_second=1,
        start_time=start_time,
        end_time=end_time,
        limit=5,
        is_asc=True,
        is_gzip=False
    )
    logging.info(f"获取长度 {len(result[0])} 条数据")
    for item in reversed(result[0]):
        logging.info(f"{item['Time']}")