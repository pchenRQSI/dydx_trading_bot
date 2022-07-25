#dydx_trading_bot

## Requirements:
requirements.txt


## Run:
main.py

## Documentation:
### Configs:
configuration of the api and the trading bot

### on_tick:
the function that is called every tick

### order:
create, cancel and modify orders

### parse_message:
parse message send by websocket, there are two types of message:
1. orderbook message: the message contains the orderbook update
2. order message: whenever there is a creation, cancellation or modification of an order

## API Documentation:
https://docs.dydx.exchange/?python#creating-and-signing-requests

## How To Generate API Key for DYDX Testnet:

1. Create a new account on Metamask and DYDX Testnet.
https://www.youtube.com/watch?v=4KZJPac9nJs
!!! Make sure your select Ropsten test Network in Metamask and testnet on dydx here is how you do it (http://www.herongyang.com/Ethereum/MetaMask-Extension-Add-Ropsten-Test-Network.html)
2. Get the dydx API from Webinterface of dydx, here is how you do it (https://www.youtube.com/watch?v=F6dsHxpkwGY)
3. Copy the API key and secret key from the Webinterface of basic_config.py
4. If you face any trouble setting this up, Peiren can help you with it.

