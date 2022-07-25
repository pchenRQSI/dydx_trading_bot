from dydx3 import Client
from configs.basic_config import *

private_client = Client(
                        host=host,
                        api_key_credentials={ 'key': key,
                                             'secret':secret,
                                             'passphrase': passphrase},
                        stark_private_key=stark_private_key,
                        default_ethereum_address=ethereum_address,
                        network_id=network_id
                        )