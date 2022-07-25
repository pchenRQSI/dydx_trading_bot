from run_tick import run_script
import time

if __name__ == '__main__':

    while True:
        try:
            run_script()
        except Exception as e:
            raise e
            print(e)
            print('sleep 5 sec before re-start websocket')
            time.sleep(5)
            continue

