import errno
from time import sleep

from escpos.printer import Network
import subprocess
import re
import requests
import socket
import queue
from threading import Thread
tout = 20
print_queue = queue.Queue()


def print_handler():
    while True:
        item = print_queue.get()
        try:
            # Get length of image
            # Connect to printer
            printer = Network(item['ip'], port=9100)
            # Print image
            printer.open()
            printer.set(align='center', width=2, height=2)
            printer.image(item['image'])
            printer.cut()
            printer.close()
            sleep(6)
        except Exception as e:
            print("Printer queue error", e)
        # Handle errors

        print_queue.task_done()


def print_base64(image_path, db):
    try:  # Connect to the printer
        data = db.getall()
        for key in data:
            if db.get(key) != "None":
                ip = db.get(key)
                break
        print_queue.put({
            'image': image_path,
            'ip': ip
        })
        return True
    except Exception as e:
        print(e)
        return False


def scan(rng, db, meta):
    founded_ips = []
    nmap_args = f'nmap -p 9100 --open {rng}.1-255 -M200 -oG -'
    proc = subprocess.Popen(nmap_args, shell=True, stdout=subprocess.PIPE)
    # Read and parse nmap output
    for line in proc.stdout:
        line = line.decode('utf-8')
        print(line)
        ip_pattern = r'Host:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

        match = re.search(ip_pattern, line)

        if match:
            ip = match.group(1)
            if ip not in founded_ips:
                founded_ips.append(ip)

    proc.wait()  # Wait for subprocess to exit

    for ip in founded_ips[0:10]:
        headers = {
            # 'Authorization': 'Basic admin:admin'
            'Authorization': 'Basic YWRtaW46YWRtaW4='
        }
        try:
            print("Checking", ip)
            res = requests.get("http://" + ip + '/status_en.html', headers=headers, timeout=tout)
            mac = str(res.content).split('var cover_sta_mac = "')[1].split('";')[0]
            db.set(mac, ip)
            attr = meta.get(mac) if meta.get(mac) else {}
            attr['type'] = 'wifi'
            meta.set(mac, attr)
            meta.dump()
            db.dump()
        except:
            print("Printer doesn't have Wifi Connection")
            socket.setdefaulttimeout(5)
            response = socket.socket()
            response.connect((ip, 80))

            request = f"GET /ip_info.htm HTTP/1.1\r\nHost: {ip}\r\n\r\n"
            response.send(request.encode('utf-8'))

            html = b""
            try:
                while True:
                    data = response.recv(1024)
                    if not data:
                        break
                    html += data
            except:
                continue
            try:
                response.shutdown(socket.SHUT_RD)
                response.close()
                mac_pattern = r'..-..-..-..-..-..'
                match = re.search(mac_pattern, str(html))
                if match:
                    mac = match.group()
                    mac = mac.replace("-", ':')
                    db.set(mac, ip)
                    attr = meta.get(mac) if meta.get(mac) else {}
                    attr['type'] = 'lan'
                    meta.set(mac, attr)
                    meta.dump()

                    data = db.getall()
                    for key in data:
                        if key != mac and db.get(key) == ip:
                            db.set(key, "None")
                    db.dump()
            except:
                print("Socket not found")

            else:
                print("MAC ADDR not found")

            pass
    data = db.getall()
    # for key in data:
    #     if db.get(key) not in founded_ips:
    #         db.set(key, "None")
    #         db.dump()
    return data


def is_online(ip, port):
    try:
        socket.create_connection((ip, port), 2)
        return True
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            return False
        else:
            print(f"Error: {e}")
            return False


def connect_to_wifi(mac, wifi, db):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{db.get(mac)}',
        'Referer': f'http://{db.get(mac)}/wireless_en.html',

    }
    ip = db.get(mac)
    ssid = wifi.get("SSID")
    password = wifi.get("PASSWORD")
    payload = f'sta_setting_encry=AES&sta_setting_auth=WPA2PSK&sta_setting_ssid={ssid}&sta_setting_auth_sel=WPA2PSK&sta_setting_encry_sel=AES&sta_setting_type_sel=ASCII&sta_setting_wpakey={password}&wan_setting_dhcp=DHCP'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                             timeout=tout)

    except Exception as e:
        print(e)
        print("HTTP request to printer to set wifi credentials failed.")
        pass

def hard_reset_printer(mac, db):
    # Command : 1f 1b 1f 27 13 14 52 00
    # reset printer
    ip = db.get(mac)
    p = Network(ip, port=9100)
    # Open connection
    p.open()

    # Reset command
    p.text('\x1f\x1b\x1f\x27\x13\x14\x52\x00')

    # Close connection
    p.close()