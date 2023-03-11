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
import copy

import octobot_commons.channels_name as channels_name
import octobot_commons.enums as commons_enums
import octobot_commons.databases as commons_databases
import octobot_commons.display as commons_display
import octobot_commons.logging as commons_logging

import octobot_trading.enums as enums
import octobot_trading.storage.abstract_storage as abstract_storage
import octobot_trading.storage.util as storage_util
import octobot_trading.personal_data.orders.order_factory as order_factory


class OrdersStorage(abstract_storage.AbstractStorage):
    LIVE_CHANNEL = channels_name.OctoBotTradingChannelsName.ORDERS_CHANNEL.value
    HISTORY_TABLE = commons_enums.DBTables.ORDERS.value
    IS_HISTORICAL = False

    def __init__(self, exchange_manager, plot_settings: commons_display.PlotSettings,
                 use_live_consumer_in_backtesting=None, is_historical=None):
        super().__init__(exchange_manager, plot_settings=plot_settings,
                         use_live_consumer_in_backtesting=use_live_consumer_in_backtesting, is_historical=is_historical)
        self.startup_orders = {}

    def should_register_live_consumer(self):
        # live orders should only be stored on real trading
        return self._should_store_date()

    def _should_store_date(self):
        return not self.exchange_manager.is_trader_simulated \
            and not self.exchange_manager.is_backtesting

    async def on_start(self):
        await self._load_startup_orders()

    async def _live_callback(
        self,
        exchange: str,
        exchange_id: str,
        cryptocurrency: str,
        symbol: str,
        order: dict,
        is_new: bool,
        is_from_bot: bool,
    ):
        # only store the current snapshot of open orders when order updates are received
        await self._update_history()
        await self.trigger_debounced_flush()

    async def _update_history(self):
        await self._get_db().replace_all(
            self.HISTORY_TABLE,
            [
                _format_order(
                    order,
                    self.exchange_manager,
                    self.plot_settings.chart,
                    self.plot_settings.x_multiplier,
                    self.plot_settings.kind,
                    self.plot_settings.mode
                )
                for order in self.exchange_manager.exchange_personal_data.orders_manager.get_open_orders()
            ],
            cache=False,
        )

    async def _store_history(self):
        await self._update_history()
        await self._get_db().flush()

    def _get_db(self):
        return commons_databases.RunDatabasesProvider.instance().get_orders_db(
            self.exchange_manager.bot_id,
            storage_util.get_account_type_suffix_from_exchange_manager(self.exchange_manager),
            self.exchange_manager.exchange_name,
        )

    async def get_startup_order_details(self, order_id):
        return self.startup_orders.get(order_id, None)

    async def _load_startup_orders(self):
        if self._should_store_date():
            self.startup_orders = {
                order["id"]: order
                for order in copy.deepcopy(await self._get_db().all(self.HISTORY_TABLE))
                if order    # skip empty order details (error when serializing)
            }
        else:
            self.startup_orders = {}

    def get_self_startup_managed_orders_details_from_group(self, group_id):
        return [
            order
            for order in self.startup_orders.values()
            if order[enums.PersistedOrdersAttr.GROUP.value].get(enums.PersistedOrdersAttr.GROUP_ID.value, None)
            == group_id
            and order[OrdersStorage.ORIGIN_VALUE_KEY][enums.ExchangeConstantsOrderColumns.SELF_MANAGED.value]
        ]


def _get_group_dict(order, exchange_manager):
    if not order.order_group:
        return {}
    try:
        return {
            enums.PersistedOrdersAttr.GROUP_ID.value: order.order_group.name,
            enums.PersistedOrdersAttr.GROUP_TYPE.value:order.order_group.__class__.__name__
        }
    except KeyError:
        return {}


def _get_chained_orders(order, exchange_manager, chart, x_multiplier, kind, mode):
    if not order.chained_orders:
        return []
    return [
        _format_order(chained_order, exchange_manager, chart, x_multiplier, kind, mode)
        for chained_order in order.chained_orders
    ]


def create_order_from_storage_details(trader, order_details):
    return order_factory.create_order_from_dict(trader, order_details[OrdersStorage.ORIGIN_VALUE_KEY])


def _format_order(order, exchange_manager, chart, x_multiplier, kind, mode):
    try:
        return {
            OrdersStorage.ORIGIN_VALUE_KEY: OrdersStorage.sanitize_for_storage(order.to_dict()),
            enums.PersistedOrdersAttr.EXCHANGE_CREATION_PARAMS.value:
                OrdersStorage.sanitize_for_storage(order.exchange_creation_params),
            enums.PersistedOrdersAttr.TRADER_CREATION_KWARGS.value:
                OrdersStorage.sanitize_for_storage(order.trader_creation_kwargs),
            enums.PersistedOrdersAttr.SHARED_SIGNAL_ORDER_ID.value: order.shared_signal_order_id,
            enums.PersistedOrdersAttr.HAS_BEEN_BUNDLED.value: order.has_been_bundled,
            enums.PersistedOrdersAttr.ENTRIES.value: order.associated_entry_ids,
            enums.PersistedOrdersAttr.GROUP.value: _get_group_dict(order, exchange_manager),
            enums.PersistedOrdersAttr.CHAINED_ORDERS.value:
                _get_chained_orders(order, exchange_manager, chart, x_multiplier, kind, mode),
            "x": order.creation_time * x_multiplier,
            "text": f"{order.order_type.name} {order.origin_quantity} {order.currency} at {order.origin_price}",
            "id": order.order_id,
            "symbol": order.symbol,
            "trading_mode": exchange_manager.trading_modes[0].get_name(),
            "type": order.order_type.name if order.order_type is not None else enums.TraderOrderType.UNKNOWN.value,
            "volume": float(order.origin_quantity),
            "y": float(order.created_last_price),
            "cost": float(order.total_cost),
            "state": order.state.state.value if order.state is not None else enums.States.UNKNOWN.value,
            "chart": chart,
            "kind": kind,
            "side": order.side.value,
            "mode": mode,
            "color": "red" if order.side is enums.TradeOrderSide.SELL else "blue",
            "size": "10",
            "shape": "arrow-bar-left" if order.side is enums.TradeOrderSide.SELL else "arrow-bar-right"
        }
    except Exception as err:
        commons_logging.get_logger(OrdersStorage.__name__).exception(err, True, f"Error when formatting order: {err}")
    return {}
