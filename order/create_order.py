from configs.dydx_private_client import private_client
from configs.basic_config import limit_fee, market_order_expiration
from decimal import Decimal
import time
from trading_log.log import record_logs

class CreateOrder:
    def __init__(self):
        self.position_id = private_client.private.get_account().data['account']['positionId']

        #store market info, right now only store minimum tick and size and funding rate
        self.market_info = {}

    def update_market_info(self, coin):
        '''
        update the market information include funding rate and orcale price etc
        :param coin:
        :return:
        '''
        market = private_client.public.get_markets(coin).data['markets'][coin]
        self.market_info[coin] = market

    def create_market_order(self,best_bid_ask: dict, coin: str, size: str, side:str):
        if coin in best_bid_ask:
            if side == 'BUY':
                #since the order request a worset price, the price will be 20 ticks lower/higher the bid/aslk
                price =best_bid_ask[coin]['best_ask'] + Decimal(self.market_info[coin]['tickSize']) * Decimal('20')
                # create market order
                order_params = {'position_id': self.position_id, 'market': coin, 'side': side,
                                'order_type': 'MARKET', 'size': str(size), 'price': str(price), 'limit_fee': limit_fee,
                                'post_only': False, 'time_in_force': 'GTT',
                                'expiration_epoch_seconds': time.time() + market_order_expiration}
            else:
                price = best_bid_ask[coin]['best_bid'] - Decimal(self.market_info[coin]['tickSize']) * Decimal('20')
                order_params = {'position_id': self.position_id, 'market': coin, 'side': side,
                                'order_type': 'MARKET', 'size': str(size), 'price': str(price), 'limit_fee': limit_fee,
                                'post_only': False, 'time_in_force': 'GTT',
                                'expiration_epoch_seconds': time.time() + market_order_expiration}
            #get the order id
            order_id = private_client.private.create_order(**order_params).data['order']['id']
            return order_id
        else:
            record_logs('error: coin is not in the list to trade')

    def create_limit_order(self,best_bid_ask:dict, coin:str, size:str, side:str, price:str):
        if coin in best_bid_ask:
            #making sure the order price is divisible by the tick size
            price = Decimal(price).quantize(Decimal(self.market_info[coin]['tickSize']))

            if side == 'BUY':
                # create limit order
                order_params = {'position_id': self.position_id, 'market': coin, 'side': side,
                                'order_type': 'LIMIT', 'size': str(size), 'price': str(price), 'limit_fee': limit_fee,
                                'post_only': True,
                                'expiration_epoch_seconds': time.time() + market_order_expiration}
            else:
                order_params = {'position_id': self.position_id, 'market': coin, 'side': side,
                                'order_type': 'LIMIT', 'size': str(size), 'price': str(price), 'limit_fee': limit_fee,
                                'post_only': True,
                                'expiration_epoch_seconds': time.time() + market_order_expiration}
            #get the order id
            order_id = private_client.private.create_order(**order_params).data['order']['id']
            return order_id
        else:
            record_logs('error: coin is not in the list to trade')


