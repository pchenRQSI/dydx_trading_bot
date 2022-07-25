from configs.basic_config import coin_list
from decimal import Decimal

class OrderbookParser():
    def __init__(self, order_book_msg, best_bid_ask, order_book, offsets):
        self.order_book_msg = order_book_msg
        self.best_bid_ask = best_bid_ask
        self.order_book = order_book
        self.offsets = offsets
        self.coin = order_book_msg['id']

    #parse order book message
    def parse_order_book(self):
        #parse the inital subscribe message
        if self.order_book_msg['type'] == 'subscribed':
            coin = self.order_book_msg['id']
            # create book and offset for each of the coin
            coin_order_dict = {'bids': {}, 'asks': {}}
            coin_offset_dict = {}
            for side, data in self.order_book_msg['contents'].items():
                for entry in data:
                    size = Decimal(entry['size'])
                    if size > 0:
                        # get price for order book
                        price = Decimal(entry['price'])
                        coin_order_dict[side][price] = size
                        # get offset for offset dict
                        offset = int(entry['offset'])
                        coin_offset_dict[price] = offset
            # append order book by coin to aggregate order book
            self.order_book[coin] = coin_order_dict
            self.offsets[coin] = coin_offset_dict

        #parse the update message
        if self.order_book_msg['type'] == 'channel_data':
            coin = self.order_book_msg['id']
            for side, data in self.order_book_msg['contents'].items():
                # log offset of the msg_
                if side == 'offset':
                    offset = int(data)
                    continue
                else:
                    # loop through bids and ask(side)
                    for entry in data:
                        price = Decimal(entry[0])
                        amount = Decimal(entry[1])
                        # if this quote already exist and from eariler than existing offsets, ignore
                        if price in self.offsets[coin] and offset <= self.offsets[coin][price]:
                            continue
                        # else will post the quote on offsets
                        self.offsets[coin][price] = offset
                        # if the update amount is zero, take out the order from orderbook
                        if amount == 0:
                            if price in self.order_book[coin][side]:
                                del self.order_book[coin][side][price]
                                #print(f'delete {side} order with price {price}')
                        else:
                            # if it is on the order book, replace it
                            #print(f'append/replace {side} order with price {price} to amount {amount}')
                            self.order_book[coin][side][price] = amount
        return self.order_book, self.offsets

    def get_best_bid_ask(self):
        '''
        return the best bid and ask price
        '''

        # get the best bid and ask price
        best_bid = max(self.order_book[self.coin]['bids'].keys())
        best_ask = min(self.order_book[self.coin]['asks'].keys())
        self.best_bid_ask[self.coin] = {'best_bid': best_bid, 'best_ask': best_ask}
        return self.best_bid_ask

