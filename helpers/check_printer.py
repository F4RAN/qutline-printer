import socket
import random
from time import sleep
IP_ADDRESS = "192.168.1.159" 
PORT = 9100  

counter = 0
def is_printer_ready(ip,port):
    global counter
    counter += 1
    r1 = round(random.uniform(0.5, 2.0),3)
    sleep(r1)
    c1 = check_printer_status(ip,port)
    r2 = round(random.uniform(0.5, 2.0),3)
    sleep(r2)
    if not c1 and counter < 5:
        return is_printer_ready(ip,port)
    if counter >= 5:
        return False
    c2 = check_printer_status(ip,port)
    if c1 and c2:
        return True
    else:
        if counter < 5:
            return is_printer_ready(ip,port)
        else:
            return False

    

def check_printer_status(ip, port):

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((IP_ADDRESS, PORT))

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
