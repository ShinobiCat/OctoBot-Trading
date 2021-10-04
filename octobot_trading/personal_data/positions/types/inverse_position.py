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
import decimal

import octobot_trading.constants as constants
import octobot_trading.personal_data.positions.position as position_class


class InversePosition(position_class.Position):
    def update_pnl(self):
        """
        LONG_PNL = CONTRACT_QUANTITY x [(1 / ENTRY_PRICE) - (1 / MARK_PRICE)]
        SHORT_PNL = CONTRACT_QUANTITY x [(1 / MARK_PRICE) - (1 / ENTRY_PRICE)]
        """
        try:
            if self.is_long():
                self.unrealised_pnl = self.quantity * ((constants.ONE / self.entry_price) -
                                                       (constants.ONE / self.mark_price))
            elif self.is_short():
                self.unrealised_pnl = self.quantity * ((constants.ONE / self.mark_price) -
                                                       (constants.ONE / self.entry_price))
            else:
                self.unrealised_pnl = constants.ZERO
        except decimal.DivisionByZero:
            self.unrealised_pnl = constants.ZERO

    def update_initial_margin(self):
        """
        Updates position initial margin = Position quantity / (entry price x leverage)
        """
        try:
            self.initial_margin = self.quantity / (self.entry_price * self.leverage)
            self._update_margin()
        except decimal.DivisionByZero:
            self.initial_margin = constants.ZERO

    def calculate_maintenance_margin(self):
        """
        :return: Maintenance margin = (Position quantity / entry price) x Maintenance margin rate
        """
        try:
            return (self.quantity / self.entry_price) * self.get_maintenance_margin_rate()
        except decimal.DivisionByZero:
            return constants.ZERO

    def update_isolated_liquidation_price(self):
        """
        Updates isolated position liquidation price
        LONG LIQUIDATION PRICE = (ENTRY_PRICE x LEVERAGE) / (LEVERAGE + 1 - (MAINTENANCE_MARGIN_RATE x LEVERAGE))
        SHORT LIQUIDATION PRICE = (ENTRY_PRICE x LEVERAGE) / (LEVERAGE - 1 + (MAINTENANCE_MARGIN_RATE x LEVERAGE))
        """
        try:
            if self.is_long():
                self.liquidation_price = (self.entry_price * self.leverage) / \
                                         (self.leverage + constants.ONE - (
                                                 self.get_maintenance_margin_rate() * self.leverage))
            elif self.is_short():
                self.liquidation_price = (self.entry_price * self.leverage) / \
                                         (self.leverage - constants.ONE + (
                                                 self.get_maintenance_margin_rate() * self.leverage))
            else:
                self.liquidation_price = constants.ZERO
            self.update_fee_to_close()
        except (decimal.DivisionByZero, decimal.InvalidOperation):
            self.liquidation_price = constants.ZERO

    def get_bankruptcy_price(self, with_mark_price=False):
        """
        :param with_mark_price: if price should be mark price instead of entry price
        :return: Bankruptcy Price for
        Long position = (Entry Price x Leverage) / (Leverage + 1)
        Short position = (Entry Price x Leverage) / (Leverage - 1)
        """
        try:
            if self.is_long():
                return (self.mark_price if with_mark_price is None else self.entry_price * self.leverage) \
                       / (self.leverage + constants.ONE)
            elif self.is_short():
                return (self.mark_price if with_mark_price is None else self.entry_price * self.leverage) \
                       / (self.leverage - constants.ONE)
            return constants.ZERO
        except decimal.DivisionByZero:
            return constants.ZERO

    def get_order_cost(self):
        """
        :return: Order Cost = Initial margin + 2-way taker fee (fee to open + fee to close)
        """
        return self.initial_margin + self.get_two_way_taker_fee()

    def get_fee_to_open(self):
        """
        :return: Fee to open = (Quantity / Mark price ) x taker fee
        """
        try:
            return (self.quantity / self.mark_price) * self.get_taker_fee()
        except decimal.DivisionByZero:
            return constants.ZERO

    def update_fee_to_close(self):
        """
        :return: Fee to close = (Quantity / Bankruptcy Price derived from mark price) x taker fee
        """
        try:
            self.fee_to_close = (self.quantity / self.get_bankruptcy_price(with_mark_price=True)) * self.get_taker_fee()
            self._update_margin()
        except decimal.DivisionByZero:
            self.fee_to_close = constants.ZERO