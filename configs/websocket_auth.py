from dydx3.helpers.request_helpers import generate_now_iso
from configs.dydx_private_client import private_client
from configs.basic_config import *

ts = generate_now_iso()
auth_sig = private_client.private.sign(
    request_path='/ws/accounts',
    method='GET',
    iso_timestamp=ts,
    data={}
)
accounts_channel_data = {'type': 'subscribe', 'channel': 'v3_accounts', 'accountNumber': '0',
                         'apiKey': key,
                         'passphrase': passphrase,
                         'signature': str(auth_sig),
                         'timestamp': str(ts)}