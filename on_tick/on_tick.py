from configs.basic_config import refresh_orders_interval, new_positions_interval, coin_list
import time
from dydx3.helpers.request_helpers import generate_now_iso
from order.create_order import CreateOrder
from order.cancel_order import CancelOrder
from decimal import Decimal
from configs.dydx_private_client import private_client
from order.dynamic_order import DynamicOrder
from trading_log.log import record_logs, log_filled

class TickExecution(DynamicOrder):
    def get_positions(self):
        '''
        get the current positions of the account
        :return:
        '''
        active_positions = private_client.private.get_positions(status='OPEN').data['positions']
        for position in active_positions:
            coin = position['market']
            side = position['side']
            size = position['size']
            if side == 'BUY':
                self._active_positions[coin] = Decimal(size)
            else:
                self._active_positions[coin] = -Decimal(size)
        record_logs('active positions:')
        record_logs(self._active_positions)

    def get_trade_size(self):
        '''
        load trade file, currently manually input trade file, will eventually be read from database
        :return:
        '''
        trade_file = {"position": { "ETH-USD": 0.02, "AVAX-USD": 10.0, 'SOL-USD': -10, 'LTC-USD':-2},"current_time": "2022-07-18 13:00:00"}
        _new_position = trade_file['position']
        self._remainning_order_dict = {key: Decimal(str(_new_position.get(key,0))) - self._active_positions.get(key,0) for key in _new_position}
        record_logs('trade size for this hour:')
        record_logs(self._remainning_order_dict)

    def get_fills(self, filled_dict: dict):
        '''
        take out the fills from the self._remainning_order_dict and calculate the new slippage allowrance
        :param filled_dict:
        :return:
        '''
        if len(filled_dict) > 0:
            record_logs(f'old slippage allowrance is {self._dollar_slippage_allowed}')
            for coin in filled_dict.keys():
                order_id = filled_dict[coin]['id']
                amount = Decimal(filled_dict[coin]['amount'])
                side = filled_dict[coin]['side']
                type = filled_dict[coin]['type']
                price = Decimal(filled_dict[coin]['price'])
                liquidity = filled_dict[coin]['liquidity']
                fee = Decimal(filled_dict[coin]['fee'])
                if side == 'BUY':
                    self._remainning_order_dict[coin] -= amount
                    dollar_cost = (price - self._first_tick_price_dict[coin]) * amount
                    self._long_filled = self._long_filled + self._first_tick_price_dict[coin] * amount
                else:
                    self._remainning_order_dict[coin] += amount
                    dollar_cost = (self._first_tick_price_dict[coin] - price) * amount
                    self._short_filled = self._short_filled + self._first_tick_price_dict[coin] * amount

                self._dollar_slippage_allowed = self._dollar_slippage_allowed - dollar_cost - fee
                record_logs( f'order of coin {coin} is a {liquidity} order, with price {price} and open price {self._first_tick_price_dict[coin]} has dollar cost {dollar_cost} and fee {fee}, '
                             f'new slippage allowrance is {self._dollar_slippage_allowed}')

                filled_info_list = [generate_now_iso(),
                                    self._first_tick_time,
                                    order_id,
                                    coin,
                                    amount,
                                    self._required_amount,
                                    type,
                                    price,
                                    fee,
                                    self._first_tick_price_dict[coin],
                                    liquidity
                                    ]
                log_filled(filled_info_list)

        #record_logs('remainning order dict:')
        #record_logs(self._remainning_order_dict)


    def log_first_tick_price(self, best_bid_ask):
        '''
        log the price of first tick of the hour
        :return:
        '''
        self._first_tick_time = generate_now_iso()
        for coin in self._remainning_order_dict.keys():
            self._first_tick_price_dict[coin] = (best_bid_ask[coin]['best_bid']+best_bid_ask[coin]['best_ask'])/2

    def on_tick(self, best_bid_ask, ts_refresh, ts_position):
        current_ts = time.time()
        #every hour get the new position
        if current_ts - ts_position >= new_positions_interval:
            record_logs('get new positions')
            #get position to trade in this hour
            self.get_positions()
            self.get_trade_size()
            #log the price for first tick
            self.log_first_tick_price(best_bid_ask)
            record_logs('start trading, cancel all existing orders:')
            # get all existing orders
            order_cancellation = CancelOrder()
            active_order_list = order_cancellation.active_order_list()
            # cancel all existing orders, and reloop again
            if len(active_order_list) > 0:
                order_cancellation.cancel_all_orders()
                return ts_refresh, ts_position

            self.calc_long_short_leg_required_amount()
            self.log_required_amount()
            self.calc_dollar_slippage()
            self.dynamic_order(best_bid_ask)
            ts_position = current_ts
            ts_refresh = current_ts

        #every minute refresh the orderbook
        else:
            if current_ts - ts_refresh >= refresh_orders_interval:
                record_logs('refresh orders, cancel all existing orders')
                record_logs(generate_now_iso())
                #get all existing orders
                order_cancellation = CancelOrder()
                active_order_list = order_cancellation.active_order_list()
                #cancel all existing orders, and reloop again
                if len(active_order_list) > 0:
                    order_cancellation.cancel_all_orders()
                    return ts_refresh, ts_position

                #create new orders
                self.dynamic_order(best_bid_ask)
                ts_refresh = current_ts

        return ts_refresh, ts_position