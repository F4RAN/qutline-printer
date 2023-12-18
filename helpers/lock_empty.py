import os
import threading
from time import sleep

lock = threading.Lock()


def empty_folder_periodically():
    while True:
        lock.acquire()
        print("Lock acquired")
        # delete all images in images folder
        path = 'images/'
        files = os.listdir(path)
        for file in files:
            if file.endswith('.md'):
                continue
            os.remove(path + file)
        print("Folder emptied")
        lock.release()
        sleep(60 * 60 * 24)


def run():
    th = threading.Thread(target=empty_folder_periodically)
    th.daemon = True
    th.start()

