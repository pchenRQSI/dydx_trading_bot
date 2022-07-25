

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
        print(f'{type} order creating: {order_id} market: {market} side: {side} price: {price} amount: {amount}')

    def order_created_event(self, order):
        #log when order is created
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        print(f'{type} order created: {order_id} market: {market} side: {side} price: {price} amount: {amount}')
        return order_id

    def order_filled_event(self, order):
        #log when order is filled
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        remaining_size = order['remainingSize']
        print(f'{type} order filled: {order_id} market: {market} side: {side} price: {price} amount: {amount}, remaining size: {remaining_size}')
        return order_id

    def order_cancelled_event(self, order):
        #log when order is cancelled
        type = order['type']
        order_id = order['id']
        market = order['market']
        side = order['side']
        price = order['price']
        amount = order['size']
        print(f'{type} order cancelled: {order_id} market: {market} side: {side} price: {price} amount: {amount}')
        return order_id


    def parse_order_event(self):
        #see if there is fills, if not it is a order created event
        orders = self.message['contents']['orders']
        for order in orders:
            if order['status'] == 'PENDING':
                self.order_creating_event(order)
            elif order['status'] == 'OPEN':
                order_id = self.order_created_event(order)
            elif order['status'] == 'FILLED':
                order_id = self.order_filled_event(order)
            elif order['status'] == 'CANCELED':
                order_id = self.order_cancelled_event(order)
            else:
                print(f'unknown order status: {order["status"]}')




