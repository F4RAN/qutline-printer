import os
from time import sleep


def restart_server():
    sleep(2)
    os.system("ps aux | grep app.py | grep -v grep | awk '{print $2}' | xargs kill -9")
    while True:
        print('Trying to run again')
        sleep(5)
        try:
            os.system('python3 app.py run 2> debug.txt')
            break
        except Exception as e:
            print(e)

restart_server()