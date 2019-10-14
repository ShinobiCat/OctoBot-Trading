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
#  License along with this library.
from asyncio import CancelledError

from octobot_channels.constants import CHANNEL_WILDCARD

from octobot_trading.channels.exchange_channel import ExchangeChannel, ExchangeChannelProducer, ExchangeChannelConsumer


class OrderBookProducer(ExchangeChannelProducer):
    async def push(self, symbol, asks, bids):
        await self.perform(symbol, asks, bids)

    async def perform(self, symbol, asks, bids):
        try:
            if self.channel.get_filtered_consumers(symbol=CHANNEL_WILDCARD) or self.channel.get_filtered_consumers(symbol=symbol):  # and symbol_data.order_book_is_initialized()
                self.channel.exchange_manager.get_symbol_data(symbol).handle_order_book_update(asks, bids)
                await self.send(symbol=symbol, asks=asks, bids=bids)
        except CancelledError:
            self.logger.info("Update tasks cancelled.")
        except Exception as e:
            self.logger.error(f"exception when triggering update: {e}")
            self.logger.exception(e)

    async def send(self, symbol, asks, bids):
        for consumer in self.channel.get_filtered_consumers(symbol=symbol):
            await consumer.queue.put({
                "exchange": self.channel.exchange_manager.exchange.name,
                "symbol": symbol,
                "asks": asks,
                "bids": bids
            })


class OrderBookChannel(ExchangeChannel):
    PRODUCER_CLASS = OrderBookProducer
    CONSUMER_CLASS = ExchangeChannelConsumer
