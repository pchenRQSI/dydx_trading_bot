from configs.dydx_private_client import private_client
from trading_log.log import record_logs

class CancelOrder:
    '''
    class to get active orders and cancel orders
    '''
    def __init__(self):
        pass

    def active_order_list(self):
        active_order_list = private_client.private.get_orders().data['orders']
        record_logs(f'there are {len(active_order_list)} active orders')
        return active_order_list

    def cancel_all_orders(self):
        order_list = private_client.private.cancel_all_orders()
        record_logs('cancelling all orders...')