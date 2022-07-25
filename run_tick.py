import json
import websocket
import time
from configs.basic_config import coin_list
from configs.websocket_auth import accounts_channel_data
from parse_message.parse_orderbook import OrderbookParser
from parse_message.parse_order_event import OrderEventParser
from on_tick import on_tick


# create dict to store orderbook
order_list = [{}] * len(coin_list)
order_book = dict(zip(coin_list, order_list))

# create dict to store offset
offsets = dict(zip(coin_list, order_list))

# get the best bid and ask price
best_bid_ask = dict(zip(coin_list, order_list))

#time stamp to refresh the orderbook
ts_refresh = 0

#time stamp to get new position
ts_position = 0

def run_script():

    def on_open(ws):
        print('opened')
        #subscribe to order books of all the coins
        for coin in coin_list:
            order_book_data = {'type':'subscribe','channel':'v3_orderbook','id':coin,'includeOffsets':'True'}
            ws.send(json.dumps(order_book_data))

        #subscribe to account activities
        ws.send(json.dumps(accounts_channel_data))

    def on_error(ws, error):
        print(error)
        raise error

    def on_message(ws, message):
        #use global so that function can assess global variables
        global order_book, offsets, best_bid_ask, ts_refresh, ts_position, active_order_set

        #parse message from websocket
        obj = json.loads(message)
        if obj['type'] != 'connected':
            #parse orderbook data
            if obj['channel'] == 'v3_orderbook':
                parser = OrderbookParser(obj, best_bid_ask, order_book, offsets)
                order_book, offsets = parser.parse_order_book()
                best_bid_ask = parser.get_best_bid_ask()
                #print(best_bid_ask)

            #parse account activity data, include order creation, order cancellation, order fill etc
            if obj['channel'] == 'v3_accounts':
                print(obj)
                parser = OrderEventParser(obj)
                parser.parse_order_event()


        #execute on_tick to make orders only when the orderbook is updated
        if all(best_bid_ask.values()):
            ts_refresh, ts_position = on_tick(best_bid_ask, ts_refresh, ts_position)
        else:
            print('best bid and ask not ready')


    def on_close(ws, close_status_code, close_msg):
        print('closed')

    socket = 'wss://api.stage.dydx.exchange/v3/ws'
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()