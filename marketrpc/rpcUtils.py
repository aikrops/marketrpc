import json
import time
import grpc
import logging
from datetime import datetime
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# utils_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.append(utils_dir)
import market_history_pb2
import market_history_pb2_grpc

logging.basicConfig(level=logging.INFO,format="[%(name)s][%(asctime)s][%(filename)s:%(lineno)d]\t%(levelname)s\t%(message)s",)

GRPC_SERVER_ADDRESS = '10.100.52.41:19999'
GRPC_OPTION = [('grpc.max_send_message_length', 100 * 1024 * 1024),('grpc.max_receive_message_length', 100 * 1024 * 1024)]

def datetime_to_millis(date_str: str) -> int:
    """
    将日期时间字符串转换为毫秒级时间戳

    :param date_str: 日期时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'。
                     如果输入格式不正确或字符串为空，则会抛出 ValueError。
    :return: 毫秒级时间戳
    :raises ValueError: 如果输入的日期时间字符串格式不正确或为空。
    """
    if not date_str:
        raise ValueError("日期时间字符串不能为空")
    
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        if len(date_str) == 10:
            date_str = date_str + " 00:00:00"
        date_obj = datetime.strptime(date_str, date_format)
        timestamp_sec = date_obj.timestamp()
        timestamp_millisec = int(timestamp_sec * 1000)
    except ValueError as e:
        raise ValueError(f"无效的日期时间格式 '{date_str}': {e}")

    return timestamp_millisec

def calculate_percentage(start_time, end_time, curr_time):
    """
    计算当前时间戳在给定时间范围内的百分比

    :param start_time: 开始时间戳
    :param end_time: 结束时间戳
    :param curr_time: 当前时间戳
    :return: 当前时间戳在给定时间范围内的百分比
    """
    if curr_time <= start_time:
        return 0
    if curr_time >= end_time:
        return 100
    
    percentage = ((curr_time - start_time) / (end_time - start_time)) * 100
    return percentage

# 查询市场K线数据。
def market_kline(
    account_type: str,
    symbol: str,
    kline_interval_second: int,
    start_time: any,
    end_time: any,
    start_id: int = 0,
    end_id: int = 0,
    schema: str = "BINANCE",
    type: str = "KLINE",
    limit: int = 10000,
    exchange: str = "BINANCE",
    is_asc: bool = True,
    is_gzip: bool = False,
    debug: bool = False
):
    """
    查询市场K线数据(倒序输出)

    :param schema: 模式名，币安：BINANCE，A股：ASTOCK，(default:BINANCE)
    :param type: 数据类型，(default: KLINE)
    :param exchange: 交易所名称，币安：BINANCE，A股票：1, (default:binance)
    :param account_type: 账户类型，币安：future/spot，A股上证：1，A股票深证：2
    :param symbol: 交易对，加密货币支持列表(adausdt, bnbusdt, btcusdt, dogeusdt, ethusdt, solusdt, xrpusdt)，股票个股交易对(交易代码 000001 600519)
    :param kline_interval_second: K线时间间隔，币安1s，A股60s，(default:1)
    :param start_time: 开始时间戳
    :param end_time: 结束时间戳
    :param start_id: 开始ID
    :param end_id: 结束ID
    :param limit: 数据限制数量(default:10000)
    :param is_asc: 是否升序排列
    :param is_gzip: 是否使用gzip压缩
    :param debug: 是否开启调试模式
    :return Time: 标准上海时间
    :return Timestamp: 时间戳
    :return IntervalSecond: K线时间间隔(1秒,1分钟,1小时)
    :return Open: 开盘价
    :return High: 最高价
    :return Low: 最低价
    :return Close: 收盘价
    :return Volume: 成交量
    :return EndTimestamp: 结束时间戳
    :return TransactionNumber: 成交笔数
    :return TransactionVolume: 成交额
    :return BuyTransactionVolume: 买单成交额
    :return BuyTransactionAmount: 买单成交笔数
    :return StartId: 开始ID
    :return EndId: 结束ID
    """

    if not exchange:
        raise ValueError("Exchange Exception Error.")
    if not account_type:
        raise ValueError("Account type cannot be empty.")
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if isinstance(start_time, str):
        start_time = datetime_to_millis(start_time)
    elif isinstance(start_time, int):
        if len(str(start_time)) == 10:
            start_time = int(start_time) * 1000
        elif len(str(start_time)) == 13:
            start_time = int(start_time)
        else:
            raise ValueError("Start time must be in seconds or milliseconds.")
    if isinstance(end_time, str):
        end_time = datetime_to_millis(end_time)
    elif isinstance(end_time, int):
        if len(str(end_time)) == 10:
            end_time = int(end_time) * 1000
        elif len(str(end_time)) == 13:
            end_time = int(end_time)
        else:
            raise ValueError("End time must be in seconds or milliseconds.")
    if start_time > end_time:
        raise ValueError("Start time must be less than or equal to end time.")
    if kline_interval_second <= 0:
        raise ValueError("Kline interval second must be greater than 0.")
    if not 1 <= limit <= 10000:
        raise ValueError("Limit must be between 1 and 10000.")
    
    timerStartTimestamp = time.time()

    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        stub = market_history_pb2_grpc.MarketHistoryServiceStub(channel)

        json_data = json.dumps({
            "schema": schema.upper(),
            "exchange": exchange.upper(),
            "account_type": account_type.upper(),
            "symbol": symbol.upper(),
            "kline_interval_second": kline_interval_second,
            "start_time": start_time,
            "end_time": end_time,
            "start_id": start_id,
            "end_id": end_id,
            "limit": limit,
            "is_asc": is_asc,
            "is_gzip": is_gzip,
            "debug": debug
        })

        data_request = market_history_pb2.DataRequest(
            type=type,
            jsonData=json_data
        )

        if debug:
            logging.info(f"data_request - type: {type}, json_data: {json_data}")

        try:
            response = stub.queryData(data_request)
            timerEndTimestamp = time.time()
            logging.info(f"Time elapsed: {timerEndTimestamp - timerStartTimestamp:.2f} seconds")
        except grpc.RpcError as e:
            logging.error(f"gRPC request failed with code {e.code()}: {e.details()}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

        # grpc 调试
        # logging.info(f"Code: {response.code}, Message: {response.msg}, Success: {response.success}, Type: {response.type}, JSON Data: {response.jsonData}")

        try:
            json_data = json.loads(response.jsonData)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON: {e}")
            raise ValueError("Failed to decode JSON from server response.") from e

        market_kline_list = []

        if not isinstance(json_data, dict) or "data" not in json_data:
            logging.error(f"Invalid JSON response: {json_data}")
            raise ValueError("Invalid JSON response format.")
        else:
            market_kline_list.append(json_data["data"])
            return market_kline_list
    
# 查询市场成交流数据
def market_aggtrade(
    exchange: str,
    account_type: str,
    symbol: str,
    start_time: int,
    end_time: int,
    start_id: int = 0,
    end_id: int = 0,
    schema: str = "BINANCE",
    type: str = "AGG_TRADE",
    limit: int = 10000,
    is_asc: bool = True,
    is_gzip: bool = False,
    debug: bool = False
): 
    """
    查询市场交易数据(正序输出)

    :param type: 数据类型(default:AGG_TRADE)
    :param exchange: 交易所名称
    :param account_type: 账户类型
    :param symbol: 交易对
    :param start_time: 开始时间戳
    :param end_time: 结束时间戳
    :param start_id: 开始ID
    :param end_id: 结束ID
    :param limit: 数据限制数量(default:10000)
    :param is_asc: 是否升序排列
    :param is_gzip: 是否使用gzip压缩
    :return Time: 标准上海时间
    :return Timestamp: 时间戳
    :return AId: 数据id
    :return First: 成交流first
    :return Last: 成交流last
    :return Price: 价格
    :return Quantity: 数量
    :return IsBuyer: bool类型(True|False)
    """
    if not exchange:
        raise ValueError("Exchange Exception Error.")
    if not account_type:
        raise ValueError("Account type cannot be empty.")
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if isinstance(start_time, str):
        start_time = datetime_to_millis(start_time)
    elif isinstance(start_time, int):
        if len(str(start_time)) == 10:
            start_time = int(start_time) * 1000
        elif len(str(start_time)) == 13:
            start_time = int(start_time)
        else:
            raise ValueError("Start time must be in seconds or milliseconds.")
    if isinstance(end_time, str):
        end_time = datetime_to_millis(end_time)
    elif isinstance(end_time, int):
        if len(str(end_time)) == 10:
            end_time = int(end_time) * 1000
        elif len(str(end_time)) == 13:
            end_time = int(end_time)
        else:
            raise ValueError("End time must be in seconds or milliseconds.")
    if start_time > end_time:
        raise ValueError("Start time must be less than or equal to end time.")
    if not 1 <= limit <= 10000:
        raise ValueError("Limit must be between 1 and 10000.")
    
    timerStartTimestamp = time.time()

    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        stub = market_history_pb2_grpc.MarketHistoryServiceStub(channel)

        json_data = json.dumps({
            "schema": schema.upper(),
            "exchange": exchange.upper(),
            "account_type": account_type.upper(),
            "symbol": symbol.upper(),
            "start_time": start_time,
            "end_time": end_time,
            "start_id": start_id,
            "end_id": end_id,
            "limit": limit,
            "is_asc": is_asc,
            "is_gzip": is_gzip,
            "debug": debug
        })

        data_request = market_history_pb2.DataRequest(
            type=type,
            jsonData=json_data
        )

        if debug:
            logging.info(f"data_request - type: {type}, json_data: {json_data}")

        try:
            response = stub.queryData(data_request)
            timerEndTimestamp = time.time()
            logging.info(f"Time elapsed: {timerEndTimestamp - timerStartTimestamp:.2f} seconds")
        except grpc.RpcError as e:
            logging.error(f"gRPC request failed with code {e.code()}: {e.details()}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

        try:
            json_data = json.loads(response.jsonData)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON: {e}")
            raise ValueError("Failed to decode JSON from server response.") from e

        market_aggtrade_list = []

        if not isinstance(json_data, dict) or "data" not in json_data:
            logging.error(f"Invalid JSON response: {json_data}")
            raise ValueError("Invalid JSON response format.")
        else:
            market_aggtrade_list.append(json_data["data"])
            return market_aggtrade_list

# 查询市场订单簿数据
def market_orderbook(
    exchange: str,
    account_type: str,
    symbol: str,
    start_time: int = 0,
    end_time: int = 0,
    start_id: int = 0,
    end_id: int = 0,
    schema: str = "BINANCE",
    type: str = "ORDER_BOOK",
    limit: int = 10000,
    is_asc: bool = True,
    is_gzip: bool = False,
    debug: bool = False
):
    """
    查询市场订单簿数据(正序输出)

    :param type: 数据类型(default:ORDER_BOOK)
    :param exchange: 交易所名称
    :param account_type: 账户类型
    :param symbol: 交易对
    :param start_id: 开始ID
    :param end_id: 结束ID
    :param start_time: 开始时间戳
    :param end_time: 结束时间戳
    :param limit: 数据限制数量(default:10000)
    :param is_asc: 是否升序排列
    :param is_gzip: 是否使用gzip压缩
    :return Time: 标准上海时间
    :return Timestamp: 时间戳
    :return UId: u_id
    :return PreUId: pre_u_id
    :return Bids: 买单
    :return Asks: 卖单
    """

    if not exchange:
        raise ValueError("Exchange Exception Error.")
    if not account_type:
        raise ValueError("Account type cannot be empty.")
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if isinstance(start_time, str):
        start_time = datetime_to_millis(start_time)
    elif isinstance(start_time, int):
        if len(str(start_time)) == 10:
            start_time = int(start_time) * 1000
        elif len(str(start_time)) == 13:
            start_time = int(start_time)
        else:
            raise ValueError("Start time must be in seconds or milliseconds.")
    if isinstance(end_time, str):
        end_time = datetime_to_millis(end_time)
    elif isinstance(end_time, int):
        if len(str(end_time)) == 10:
            end_time = int(end_time) * 1000
        elif len(str(end_time)) == 13:
            end_time = int(end_time)
        else:
            raise ValueError("End time must be in seconds or milliseconds.")
    if start_time > end_time:
        raise ValueError("Start time must be less than or equal to end time.")
    if not 1 <= limit <= 10000:
        raise ValueError("Limit must be between 1 and 10000.")

    timerStartTimestamp = time.time()

    with grpc.insecure_channel(GRPC_SERVER_ADDRESS,options=GRPC_OPTION) as channel:
        stub = market_history_pb2_grpc.MarketHistoryServiceStub(channel)

        json_data = json.dumps({
            "schema": schema.upper(),
            "exchange": exchange.upper(),
            "account_type": account_type.upper(),
            "symbol": symbol.upper(),
            "start_id": start_id,
            "end_id": end_id,
            "start_time": start_time,
            "end_time": end_time,
            "limit": limit,
            "is_asc": is_asc,
            "is_gzip": is_gzip
        })

        data_request = market_history_pb2.DataRequest(
            type=type,
            jsonData=json_data
        )

        if debug:
            logging.info(f"data_request - type: {type}, json_data: {json_data}")

        try:
            response = stub.queryData(data_request)
            timerEndTimestamp = time.time()
            logging.info(f"Time elapsed: {timerEndTimestamp - timerStartTimestamp:.2f} seconds")
        except grpc.RpcError as e:
            logging.error(f"gRPC request failed with code {e.code()}: {e.details()}")
            raise market_history_pb2_grpc.MarketHistoryServiceStub(f"Failed to fetch market orderbook: {e.details()}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise market_history_pb2_grpc.MarketHistoryServiceStub("An unexpected error occurred during the gRPC request.") from e

        try:
            json_data = json.loads(response.jsonData)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON: {e}")
            raise ValueError("Failed to decode JSON from server response.") from e

        market_orderbook_list = []

        if not isinstance(json_data, dict) or "data" not in json_data:
            logging.error(f"Invalid JSON response: {json_data}")
            raise ValueError("Invalid JSON response format.")
        else:
            market_orderbook_list.append(json_data["data"])
            return market_orderbook_list
