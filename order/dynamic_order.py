from order.create_order import CreateOrder
from configs.basic_config import coin_list, fee_market, fee_limit, slippage_allowed, slippage_premium
from decimal import Decimal, DivisionByZero
import numpy as np
from trading_log.log import record_logs

class DynamicOrder(CreateOrder):
    def __init__(self):
        super().__init__()
        self._active_positions = {}

        #log the remainning orders needed to be traded
        self._remainning_order_dict = {}

        #log the price of first tick of the hour
        self._first_tick_time = None
        self._first_tick_price_dict = {}

        # calculate the dollar value of slippage allowed
        self._dollar_slippage_allowed = Decimal('0')

        # log the dollar amount filled for both long leg and short leg
        self._long_filled = Decimal('0')
        self._short_filled = Decimal('0')

        # log total amount needed to be filled both long leg and short leg
        self.total_long = Decimal('0')
        self.total_short = Decimal('0')

        # log the total amount required to be filled
        self._required_amount = Decimal('0')

        # start by placing limit orders 14 bps above sell order and 14 bps blew buy order
        self._slippage_premium = slippage_premium

    def calc_long_short_leg_required_amount(self):
        '''
        calculate the required amount for each leg
        '''
        #reset the total long and short and filled
        self._long_filled = Decimal('0')
        self._short_filled = Decimal('0')
        self.total_long = Decimal('0')
        self.total_short = Decimal('0')
        #calculate the required amount for each leg
        for key in self._remainning_order_dict:
            required_fill = abs(self._remainning_order_dict[key]) * self._first_tick_price_dict[key]
            # if required_fill is smaller than 20 dollars, don't fill it
            if required_fill < Decimal('20'):
                record_logs(f"{key}'s order with starting price {self._first_tick_price_dict[key]} and amount{self._remainning_order_dict[key]} is smaller than 20 dollars, don\'t fill it")
                self._remainning_order_dict[key] = Decimal('0')
                continue
            else:
                if self._remainning_order_dict[key] > Decimal('0'):
                    record_logs(f"{key}'s order with starting price {self._first_tick_price_dict[key]} and amount{self._remainning_order_dict[key]} is buy order, fill it")
                    self.total_long = self.total_long + required_fill
                elif self._remainning_order_dict[key] < Decimal('0'):
                    record_logs(f"{key}'s order with starting price {self._first_tick_price_dict[key]} and amount{self._remainning_order_dict[key]} is sell order, fill it")
                    self.total_short = self.total_short + required_fill
                else:
                    continue
        record_logs(f'the long required amount is {self.total_long}')
        record_logs(f'the short required amount is {self.total_short}')

    # log the total amount required to be filled
    def log_required_amount(self):
        '''
         log the total amount required to be filled
        '''
        self._required_amount = self.total_long + self.total_short
        record_logs(f'the total amount required to be filled is {self._required_amount}')

    def calc_dollar_slippage(self):
        '''
        calculate the dollar slippage allowed for each leg
        '''
        self._dollar_slippage_allowed = self._required_amount * slippage_allowed
        record_logs(f'the inital dollar slippage allowed is {self._dollar_slippage_allowed}')

    def calc_slippage_allowrance(self, scaling_factor: Decimal = Decimal('8')):
        '''
        calculate the slippage allowrance for long and short leg
        '''
        #calculate the amount left for long and short orders
        _long_left = self.total_long - self._long_filled
        _short_left = self.total_short - self._short_filled
        record_logs(f'there are {_long_left} long left and {_short_left} short left')

        #calulate the amount left in percent
        _long_left_percent = _long_left / (_long_left + _short_left)
        _short_left_percent = _short_left / (_long_left + _short_left)
        record_logs(f'there are {float(_long_left_percent)*100}% long left and {float(_short_left_percent)*100}% short left')

        #calculate percentage slippage allowrance for long and short leg
        _long_slippage_allowrance_percent = Decimal('1') / (Decimal('1') + np.exp(-scaling_factor *(_long_left_percent-Decimal('0.5'))))
        _short_slippage_allowrance_percent = Decimal('1') - _long_slippage_allowrance_percent
        record_logs(f'long slippage allowrance is {float(_long_slippage_allowrance_percent)*100}% of total dollar slippage and short slippage allowrance is {float(_short_slippage_allowrance_percent)*100}% of total dollar slippage')

        #calculate dollar slippage allowrance for long and short leg
        _long_dollar_slippage_allowrance = _long_slippage_allowrance_percent * self._dollar_slippage_allowed
        _short_dollar_slippage_allowrance = _short_slippage_allowrance_percent * self._dollar_slippage_allowed
        record_logs(f'total slippage allowed is {self._dollar_slippage_allowed}$ long slippage allowrance is {float(_long_dollar_slippage_allowrance)}$ and short slippage allowrance is {float(_short_dollar_slippage_allowrance)}$')

        #calculate slippage allowrance for long and short leg
        try:
            _long_slippage_allowrance = _long_dollar_slippage_allowrance / _long_left
        except DivisionByZero:
            _long_slippage_allowrance = Decimal('0')
        try:
            _short_slippage_allowrance = _short_dollar_slippage_allowrance / _short_left
        except DivisionByZero:
            _short_slippage_allowrance = Decimal('0')
        record_logs(f'long slippage allowrance is {float(_long_slippage_allowrance)*100}% and short slippage allowrance is {float(_short_slippage_allowrance)*100}%')

        return _long_slippage_allowrance, _short_slippage_allowrance

    def dynamic_order(self, best_bid_ask, premium_step=Decimal('0.0001')):
        '''
        place orders dynamically based on the current price and the start price, will run every minute
        '''
        # calculate the slippage allowrance for long and short leg
        _long_slippage_allowed, _short_slippage_allowed = self.calc_slippage_allowrance()

        record_logs(f'the slippage premium is {self._slippage_premium}')
        for trading_pair in coin_list:
            #update market info for each trading pair
            self.update_market_info(trading_pair)
            start_price = self._first_tick_price_dict[trading_pair]

            # order needed to be placed, in class Decimal
            curr_order_amount = self._remainning_order_dict[trading_pair]

            # determine if it is a buy or sell signal
            if curr_order_amount > Decimal('0'):
                order_price = start_price * (Decimal('1') - self._slippage_premium + _long_slippage_allowed)
                record_logs(f'the buy order price is {float(self._slippage_premium - _long_slippage_allowed)} away from start price')
                buy_price = best_bid_ask[trading_pair]['best_ask']
                record_logs(f'the buy order of {trading_pair} has a starting price of {start_price},and a order price of {order_price}')

                if order_price < buy_price:
                    record_logs(f'order price {order_price} is less than buy price{buy_price}, place limit buy order of {trading_pair} with price {order_price * (1 - fee_limit)}')
                    self.create_limit_order(best_bid_ask=best_bid_ask, coin = trading_pair,
                                            size = str(curr_order_amount) , side = 'BUY', price = str(order_price * (1 - fee_limit)))
                else:
                    if order_price * (Decimal('1') - fee_market) >= buy_price:
                        record_logs(f'order price {order_price * (1 - fee_market)} is more than buy price{buy_price}, place market buy order of {trading_pair}')
                        self.create_market_order(best_bid_ask=best_bid_ask, coin = trading_pair,size=str(curr_order_amount), side = 'BUY')
                    else:
                        record_logs(f'order price {order_price * (1 - fee_market)} is less than buy price{buy_price}, place limit buy order of {trading_pair} with price {order_price * (1 - fee_market)}')
                        self.create_limit_order(best_bid_ask=best_bid_ask, coin=trading_pair,
                                                size=str(curr_order_amount), side='BUY',
                                                price=str(order_price * (1 - fee_market)))

            elif curr_order_amount < Decimal('0'):
                order_price = start_price * (Decimal('1') + self._slippage_premium - _short_slippage_allowed)
                record_logs(f'the sell order price is {float(self._slippage_premium - _short_slippage_allowed)} away from start price')
                sell_price = best_bid_ask[trading_pair]['best_bid']
                record_logs(f'the sell order of {trading_pair} has a starting price of {start_price},and a order price of {order_price}')

                if order_price > sell_price:
                    record_logs(f'order price {order_price} is more than sell price{sell_price}, place limit sell order of {trading_pair} with price {order_price * (1 + fee_limit)}')
                    self.create_limit_order(best_bid_ask=best_bid_ask, coin=trading_pair,
                                            size=str(-curr_order_amount), side='SELL',
                                            price=str(order_price * (1 + fee_limit)))
                else:
                    if order_price * (Decimal('1') + fee_market) <= sell_price:
                        record_logs(f'order price {order_price * (1 + fee_market)} is less than sell price{sell_price}, place market sell order of {trading_pair}')
                        self.create_market_order(best_bid_ask=best_bid_ask, coin=trading_pair,
                                                 size=str(-curr_order_amount), side='SELL')
                    else:
                        record_logs(f'order price {order_price * (1 + fee_market)} is more than sell price{sell_price}, place limit sell order of {trading_pair} with price {order_price * (1 + fee_market)}')
                        self.create_limit_order(best_bid_ask=best_bid_ask, coin=trading_pair,
                                                size=str(-curr_order_amount), side='SELL',
                                                price=str(order_price * (1 + fee_market)))
            else:
                continue
        # update the slippage premium for next minute
        self._slippage_premium = Decimal('0').max(self._slippage_premium - premium_step)
