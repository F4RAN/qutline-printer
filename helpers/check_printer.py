import socket
import random
from time import sleep


def is_printer_ready(ip, port, counter=0):
    counter += 1
    r1 = random.randint(1000, 2000) / 1000
    sleep(r1)
    c1 = check_printer_status(ip, port)
    r2 = random.uniform(0,2) * random.uniform(0,2) + random.uniform(1,2)
    sleep(r2)
    print(r1,r2)
    if not c1 and counter < 5:
        return is_printer_ready(ip, port, counter)
    if counter >= 5:
        return False
    c2 = check_printer_status(ip, port)
    if c1 and c2:
        return True
    else:
        if counter < 5:
            return is_printer_ready(ip, port, counter)
        else:
            return False


def check_printer_status(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        sock.connect((ip, port))

        esc = bytes([0x1D])
        cmd = bytes([0x72])
        param = bytes([0x01])

        status_cmd = esc + cmd + param

        sock.send(status_cmd)
        status = sock.recv(32)
        sock.close()
        if status == b'\x00':
            return True
        return False
    except Exception as e:
        print("Busy")
        print(e)
        return False

    # Wait random time
