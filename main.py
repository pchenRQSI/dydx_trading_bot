from run_tick import run_script
import time
from trading_log.log import record_logs
if __name__ == '__main__':

    while True:
        try:
            run_script()
        except Exception as e:
            raise e
            record_logs(e)
            record_logs('sleep 5 sec before re-start websocket')
            time.sleep(5)
            continue

