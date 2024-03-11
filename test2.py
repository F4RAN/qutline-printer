import socket


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
