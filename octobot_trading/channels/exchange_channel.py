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
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

from octobot_channels.consumer import Consumer, InternalConsumer, SupervisedConsumer
from octobot_channels.producer import Producer
from octobot_commons.logging.logging_util import get_logger

from octobot_channels.channels.channel import Channel

from octobot_channels.constants import CHANNEL_WILDCARD
from octobot_channels.channels.channel_instances import ChannelInstances


class ExchangeChannelConsumer(Consumer):
    pass


class ExchangeChannelInternalConsumer(InternalConsumer):
    pass


class ExchangeChannelSupervisedConsumer(SupervisedConsumer):
    pass


class ExchangeChannelProducer(Producer):
    async def send(self, **kwargs) -> None:
        for consumer in self.channel.get_filtered_consumers():
            await consumer.queue.put(kwargs)

    async def pause(self) -> None:
        self.logger.debug("Pausing...")
        # Triggers itself if not already paused
        if not self.channel.is_paused:
            self.channel.is_paused = True

    async def resume(self) -> None:
        self.logger.debug("Resuming...")
        # Triggers itself if not already resumed
        if self.channel.is_paused:
            self.channel.is_paused = False


class ExchangeChannel(Channel):
    PRODUCER_CLASS = ExchangeChannelProducer
    CONSUMER_CLASS = ExchangeChannelConsumer
    WITH_TIME_FRAME = False

    SYMBOL_KEY = "symbol"
    TIME_FRAME_KEY = "time_frame"

    def __init__(self, exchange_manager):
        super().__init__()
        self.logger = get_logger(f"{self.__class__.__name__}[{exchange_manager.exchange.name}]")
        self.exchange_manager = exchange_manager
        self.exchange = exchange_manager.exchange

        self.filter_send_counter = 0
        self.should_send_filter = False

    async def new_consumer(self,
                           callback: object = None,
                           consumer_filters: dict = None,
                           consumer_instance: object = None,
                           size=0,
                           filter_size=False,
                           symbol=CHANNEL_WILDCARD):
        consumer = consumer_instance if consumer_instance else self.CONSUMER_CLASS(callback, size=size,
                                                                                   filter_size=filter_size)
        await self.__add_new_consumer_and_run(consumer, symbol=symbol, with_time_frame=self.WITH_TIME_FRAME)
        await self.__check_producers_state()
        return consumer

    async def __check_producers_state(self) -> None:  # TODO useless (bc copy of Channel.__check_producers_state)
        if not self.get_filtered_consumers() and not self.is_paused:
            self.is_paused = True
            for producer in self.get_producers():
                await producer.pause()
        elif self.get_filtered_consumers() and self.is_paused:
            self.is_paused = False
            for producer in self.get_producers():
                await producer.resume()

    def get_filtered_consumers(self, symbol=CHANNEL_WILDCARD, time_frame=CHANNEL_WILDCARD):
        return self.get_consumer_from_filters({
            self.SYMBOL_KEY: symbol,
            self.TIME_FRAME_KEY: time_frame
        })

    async def __add_new_consumer_and_run(self, consumer, symbol=CHANNEL_WILDCARD, with_time_frame=False):
        if symbol:
            symbol = CHANNEL_WILDCARD

        consumer_filters: dict = {
            self.SYMBOL_KEY: symbol,
            self.TIME_FRAME_KEY: CHANNEL_WILDCARD if with_time_frame else None
        }

        self.add_new_consumer(consumer, consumer_filters)
        await consumer.run()
        self.logger.debug(f"Consumer started for symbol {symbol}")


def set_chan(chan, name) -> None:
    chan_name = chan.get_name() if name else name

    try:
        exchange_chan = ChannelInstances.instance().channels[chan.exchange_manager.exchange.name]
    except KeyError:
        ChannelInstances.instance().channels[chan.exchange_manager.exchange.name] = {}
        exchange_chan = ChannelInstances.instance().channels[chan.exchange_manager.exchange.name]

    if chan_name not in exchange_chan:
        exchange_chan[chan_name] = chan
    else:
        raise ValueError(f"Channel {chan_name} already exists.")


def get_chan(chan_name, exchange_name) -> ExchangeChannel:
    try:
        return ChannelInstances.instance().channels[exchange_name][chan_name]
    except KeyError:
        # get_logger(ExchangeChannel.__name__).error(f"Channel {chan_name} not found on {exchange_name}")
        raise KeyError(f"Channel {chan_name} not found on {exchange_name}")


def del_chan(chan_name, exchange_name) -> None:
    try:
        if chan_name in ChannelInstances.instance().channels[exchange_name]:
            ChannelInstances.instance().channels[exchange_name].pop(chan_name, None)
    except KeyError:
        pass
