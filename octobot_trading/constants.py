#  Drakkar-Software OctoBot-Trading
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library

import octobot_trading.enums as enums

# Strings
CURRENT_PORTFOLIO_STRING = "Current Portfolio :"
CONFIG_PORTFOLIO_INFO = "info"
CONFIG_PORTFOLIO_FREE = "free"
CONFIG_PORTFOLIO_USED = "used"
CONFIG_PORTFOLIO_TOTAL = "total"
CONFIG_PORTFOLIO_MARGIN = "margin"
REAL_TRADER_STR = "[Real Trader] "
SIMULATOR_TRADER_STR = "[Simulator] "

# Trader
CONFIG_TRADING = "trading"
CONFIG_TRADER = "trader"
CONFIG_LOAD_TRADE_HISTORY = "load-trade-history"
CONFIG_TRADER_RISK = "risk"
CONFIG_TRADER_RISK_MIN = 0.05
CONFIG_TRADER_RISK_MAX = 1
CONFIG_TRADER_REFERENCE_MARKET = "reference-market"
DEFAULT_REFERENCE_MARKET = "BTC"
CURRENCY_DEFAULT_MAX_PRICE_DIGITS = 8

# Order creation
ORDER_DATA_FETCHING_TIMEOUT = 60

# Tentacles
TRADING_MODE_REQUIRED_STRATEGIES = "required_strategies"
TRADING_MODE_REQUIRED_STRATEGIES_MIN_COUNT = "required_strategies_min_count"
TENTACLES_TRADING_MODE_PATH = "Mode"

# Simulator
CONFIG_SIMULATOR = "trader-simulator"
CONFIG_STARTING_PORTFOLIO = "starting-portfolio"
SIMULATOR_CURRENT_PORTFOLIO = "simulator_current_portfolio"

# Exchange
CONFIG_EXCHANGES = "exchanges"
CONFIG_EXCHANGE_KEY = "api-key"
CONFIG_EXCHANGE_SECRET = "api-secret"
CONFIG_EXCHANGE_PASSWORD = "api-password"
CONFIG_EXCHANGE_SANDBOXED = "sandboxed"
CONFIG_EXCHANGE_FUTURE = "future"
CONFIG_EXCHANGE_MARGIN = "margin"
CONFIG_EXCHANGE_SPOT = "spot"
CONFIG_EXCHANGE_REST_ONLY = "rest_only"
CONFIG_EXCHANGE_ENCRYPTED_VALUES = [CONFIG_EXCHANGE_KEY, CONFIG_EXCHANGE_SECRET, CONFIG_EXCHANGE_PASSWORD]
DEFAULT_EXCHANGE_TIME_LAG = 10
DEFAULT_BACKTESTING_TIME_LAG = 0
INFINITE_MAX_HANDLED_PAIRS_WITH_TIMEFRAME = -1


TESTED_EXCHANGES = ["binance", "bitmax", "kucoin", "coinbasepro"]
SIMULATOR_TESTED_EXCHANGES = ["bybit"]

CONFIG_SIMULATOR_FEES = "fees"
CONFIG_SIMULATOR_FEES_MAKER = "maker"
CONFIG_SIMULATOR_FEES_TAKER = "taker"
CONFIG_SIMULATOR_FEES_WITHDRAW = "withdraw"
CONFIG_DEFAULT_FEES = 0.1
CONFIG_DEFAULT_SIMULATOR_FEES = 0

SIMULATOR_LAST_PRICES_TO_CHECK = 50

# API
API_LOGGER_TAG = "TradingApi"

# Channels
# Exchange public data
TICKER_CHANNEL = "Ticker"
MINI_TICKER_CHANNEL = "MiniTicker"
RECENT_TRADES_CHANNEL = "RecentTrade"
LIQUIDATIONS_CHANNEL = "Liquidations"
ORDER_BOOK_CHANNEL = "OrderBook"
ORDER_BOOK_TICKER_CHANNEL = "OrderBookTicker"
KLINE_CHANNEL = "Kline"
OHLCV_CHANNEL = "OHLCV"
MARK_PRICE_CHANNEL = "MarkPrice"
FUNDING_CHANNEL = "Funding"

# Exchange personal data
TRADES_CHANNEL = "Trades"
ORDERS_CHANNEL = "Orders"
BALANCE_CHANNEL = "Balance"
BALANCE_PROFITABILITY_CHANNEL = "BalanceProfitability"
POSITIONS_CHANNEL = "Positions"

# 946742400 is 01/01/2000, if trade time is lower, there is an issue.
MINIMUM_VAL_TRADE_TIME = 946688400

# Internal
MODE_CHANNEL = "Mode"

# CCXT library constants
CCXT_INFO = "info"

# Websocket constants
CONFIG_EXCHANGE_WEB_SOCKET = "web-socket"

WEBSOCKET_FEEDS_TO_TRADING_CHANNELS = {
    TICKER_CHANNEL: [enums.WebsocketFeeds.TICKER],
    MINI_TICKER_CHANNEL: [enums.WebsocketFeeds.MINI_TICKER],
    RECENT_TRADES_CHANNEL: [enums.WebsocketFeeds.TRADES],
    LIQUIDATIONS_CHANNEL: [enums.WebsocketFeeds.LIQUIDATIONS],
    ORDER_BOOK_CHANNEL: [enums.WebsocketFeeds.L2_BOOK, enums.WebsocketFeeds.L3_BOOK],
    ORDER_BOOK_TICKER_CHANNEL: [enums.WebsocketFeeds.BOOK_TICKER],
    KLINE_CHANNEL: [enums.WebsocketFeeds.KLINE],
    OHLCV_CHANNEL: [enums.WebsocketFeeds.CANDLE],
    TRADES_CHANNEL: [enums.WebsocketFeeds.TRADE],
    ORDERS_CHANNEL: [enums.WebsocketFeeds.ORDERS],
    MARK_PRICE_CHANNEL: [enums.WebsocketFeeds.MARK_PRICE],
    BALANCE_CHANNEL: [enums.WebsocketFeeds.PORTFOLIO],
    POSITIONS_CHANNEL: [enums.WebsocketFeeds.POSITION],
    FUNDING_CHANNEL: [enums.WebsocketFeeds.FUNDING]
}
