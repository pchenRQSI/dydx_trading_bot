from configs.basic_config import refresh_orders_interval, new_positions_interval, coin_list
import time
from dydx3.helpers.request_helpers import generate_now_iso
from order.create_order import CreateOrder
from order.cancel_order import CancelOrder
from decimal import Decimal

def on_tick(best_bid_ask, ts_refresh, ts_position):
    current_ts = time.time()
    #every hour get the new position
    if current_ts - ts_position > new_positions_interval:
        print('get new positions')
        ts_position = current_ts

    #every minute refresh the orderbook
    else:
        if current_ts - ts_refresh > refresh_orders_interval:
            print('refresh orders, cancel all existing orders')
            print(generate_now_iso())
            #get all existing orders
            order_cancellation = CancelOrder()
            active_order_list = order_cancellation.active_order_list()
            print(active_order_list)
            #cancel all existing orders, and reloop again
            if len(active_order_list) > 0:
                order_cancellation.cancel_all_orders()
                return ts_refresh, ts_position

            #create new orders
            order = CreateOrder(best_bid_ask)
            # submit order for each coin
            for coin in coin_list:
                order.update_market_info(coin)
                #buy_order_id = order.create_market_order(coin, '100', 'BUY')
                # use set limit order for mid price for testing purpose
                mid_price = Decimal('0.9')*(order.best_bid_ask[coin]['best_ask'] + order.best_bid_ask[coin]['best_bid']) / 2
                buy_order_id = order.create_limit_order(coin, '1', 'BUY', str(mid_price))
            ts_refresh = current_ts

    return ts_refresh, ts_position

