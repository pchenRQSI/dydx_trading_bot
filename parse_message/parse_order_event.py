from decimal import Decimal
from trading_log.log import record_logs

class OrderEventParser:
    def __init__(self, message):
        self.message = message

    def order_creating_event(self, order):
        #log when order is created
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        record_logs(f'{type} order creating: {order_id} market: {market} side: {side} price: {price} amount: {amount}')

    def order_created_event(self, order):
        #log when order is created
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        record_logs(f'{type} order created: {order_id} market: {market} side: {side} price: {price} amount: {amount}')
        return order_id

    def order_filled_event(self, order):
        #log 'order' when order is filled
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        remaining_size = order['remainingSize']
        record_logs(f'{type} order filled: {order_id} market: {market} side: {side} price: {price} amount: {amount}, remaining size: {remaining_size}')
        return order_id, market, amount, side

    def log_filled_fee(self, fill):
        '''
        log the fees spends for fills
        :param fill:
        :return:
        '''
        type = fill['type']
        order_id = fill['orderId']
        market = fill['market']
        side = fill['side']
        price = fill['price']
        amount = fill['size']
        fee = fill['fee']
        liquidity = fill['liquidity']
        return type, order_id, market, amount, side, price, fee, liquidity


    def order_cancelled_event(self, order):
        #log when order is cancelled
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        reason = order['cancelReason']
        record_logs(f'{type} order cancelled: {order_id} market: {market} side: {side} price: {price} amount: {amount}, reason: {reason}')
        return order_id


    def parse_order_event(self):
        filled_dict = {}
        if self.message['type'] == 'subscribed':
            record_logs(f'successfully subscribed to account order events')
        else:
            #see if there is fills, if not it is a order created event
            orders = self.message['contents']['orders']
            if 'fills' in self.message['contents']:
                fills = self.message['contents']['fills']
                #log the total amount was filled
                if len(fills) > 0:
                    for fill in fills:
                        type, order_id, market, amount, side, price, fee, liquidity = self.log_filled_fee(fill)
                        filled_dict[market] = {'type': type, 'id': order_id, 'amount': amount, 'side': side, 'price': price, 'fee': fee, 'liquidity': liquidity}
            for order in orders:
                if order['status'] == 'PENDING':
                    self.order_creating_event(order)
                elif order['status'] == 'OPEN':
                    order_id = self.order_created_event(order)
                elif order['status'] == 'FILLED':
                    order_id, market, amount, side = self.order_filled_event(order)
                elif order['status'] == 'CANCELED':
                    order_id = self.order_cancelled_event(order)
                else:
                    record_logs(f'unknown order status: {order["status"]}')

        return filled_dict


