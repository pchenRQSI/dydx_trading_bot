from dydx3.helpers.request_helpers import generate_now_iso
from datetime import datetime

def record_logs(string_loged):
    date = datetime.now().strftime('%Y-%m-%d')
    time = generate_now_iso()
    info = time + ':  ' + str(string_loged)
    print(info)
    with open(f'logs/{date}_log.txt', 'a+') as f:
        f.write(info + '\n')


def log_filled(filled_info_list: list):
    date = datetime.now().strftime('%Y-%m-%d')
    with open(fr'logs/{date}_fill_price.txt', 'a+') as f:
        for item in filled_info_list:
            f.write(str(item) + ',')
        f.write('\n')