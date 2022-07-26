from decimal import Decimal

# api host and network id for dydx, on test net
host = 'https://api.stage.dydx.exchange'
network_id = 3

#api credentials for private client
key = "<API KEY>"
secret = "<API SCRET>"
passphrase = "<PASS PHASE>"
stark_private_key = "<STARK PRIVATE KEY>"
ethereum_address = '<ETH ADDRESS>'

#list of coins that are going to be traded
coin_list = ['AVAX-USD','ETH-USD','SOL-USD','LTC-USD']

#limit fee for market orders and limit orders
limit_fee = 0.0005

#market order expiration time in seconds
market_order_expiration = 70

#number of seconds between refresh orders
refresh_orders_interval = 60

#number of seconds between taking new positions
new_positions_interval = 60*60

# set up slippage assumption
fee_market = Decimal('0.0005')
fee_limit = Decimal('0.0002')
slippage_allowed = Decimal('0.0003')

slippage_premium = Decimal('0.0016')