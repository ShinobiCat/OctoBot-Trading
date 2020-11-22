# cython: language_level=3
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
#  Lesser General License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
cimport octobot_trading.exchanges.connectors.abstract_websocket_connector as abstract_websocket_connector

cdef class CCXTWebsocketConnector(abstract_websocket_connector.AbstractWebsocketConnector):
    cdef public object ccxt_client
    cdef public object async_ccxt_client
    cdef object _watch_task
    cdef object last_msg
    cdef object bot_mainloop

