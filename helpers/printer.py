from time import sleep
from escpos.printer import Network
import subprocess
import re
import requests
import socket
import queue
from tinydb import TinyDB, Query, where

from helpers.check_printer import is_printer_ready

db = TinyDB('dbs/db.json')
tout = 20




def print_base64(image_path, ip):
    try:  # Connect to the printer
        if is_printer_ready(ip, 9100):
            p = Network(ip)
            p.image(image_path)
            p.cut()
            p.close()
            return True
        else:

            return False
    except Exception as e:
        print(e)
        return False


def scan(rng, setup):
    founded_ips = []
    nmap_args = f'nmap -p 9100 --open {rng}.1-255 -M200 -oG -'
    proc = subprocess.Popen(nmap_args, shell=True, stdout=subprocess.PIPE)
    # Read and parse nmap output
    for line in proc.stdout:
        line = line.decode('utf-8')
        ip_pattern = r'Host:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

        match = re.search(ip_pattern, line)

        if match:
            ip = match.group(1)
            if ip not in founded_ips:
                founded_ips.append(ip)

    proc.wait()  # Wait for subprocess to exit

    for ip in founded_ips:
        headers = {
            # 'Authorization': 'Basic admin:admin'
            'Authorization': 'Basic YWRtaW46YWRtaW4='
        }
        try:
            print("Checking", ip)
            res = requests.get("http://" + ip + '/status_en.html', headers=headers, timeout=tout)
            mac = str(res.content).split('var cover_sta_mac = "')[1].split('";')[0]
            # db.set(mac, ip)
            printers = db.search(where('type') == 'printer')
            max_num = 1
            for printer in printers:
                if printer['data']['name'].find("Printer #"):
                    max_num = max(max_num, int(printer['data']['name'].split("#")[1]))
            name = f"Printer #{max_num + 1}"
            db.insert({'data': {'mac': mac, 'ip': ip, 'type': 'wifi', 'name': name}})

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
                    printers = db.search(where('type') == 'printer')
                    max_num = 1
                    for printer in printers:
                        if printer['data']['name'].find("Printer #"):
                            max_num = max(max_num, int(printer['data']['name'].split("#")[1]))
                    name = f"Printer #{max_num + 1}"
                    db.insert({'data': {'mac': mac, 'ip': ip, 'type': 'wifi', 'name': name}})
                    q = Query()
                    conflict_printers = db.get(q.data.ip == str(ip))['data']

                    for p in conflict_printers:
                        if p['mac'] != mac and p['ip'] == ip:
                            # set None instead of ip
                            db.update({'data': {'mac': p['mac'], 'ip': "None", 'type': p['type'], 'name': p['name']}}, q.data.mac == str(p['mac']))

            except:
                print("Socket not found")

            else:
                print("MAC ADDR not found")

            pass

    result = []
    printers = db.search(where('type') == 'printer')
    for printer in printers:
        if printer['data']['ip'] in founded_ips:
            result.append(printer['data'])
        elif not setup:
            result.append(printer['data'])
    return result


def is_online(ip, port):
    try:
        socket.create_connection((ip, port), timeout=2)
        return True
    except socket.timeout:
        return False
    except socket.error as err:
        return False


# def is_online(ip):
#     parameter = '-n'
#     try:
#         response = os.system('ping {} 1 {}'.format(parameter, ip))
#         if response == 0:
#             return True
#         else:
#             return False
#     except:
#         return False

def connect_to_wifi(mac, wifi):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{db.get(mac)}',
        'Referer': f'http://{db.get(mac)}/wireless_en.html',

    }
    q = Query()
    ip = db.get(q.data.mac == str(mac))['data']['ip']
    ssid = wifi["ssid"]
    password = wifi["password"]
    payload = f'sta_setting_encry=AES&sta_setting_auth=WPA2PSK&sta_setting_ssid={ssid}&sta_setting_auth_sel=WPA2PSK&sta_setting_encry_sel=AES&sta_setting_type_sel=ASCII&sta_setting_wpakey={password}&wan_setting_dhcp=DHCP'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                             timeout=tout)

    except Exception as e:
        print(e)
        print("HTTP request to printer to set wifi credentials failed.")
        pass


def hard_reset_printer(mac):
    # Command : 1f 1b 1f 27 13 14 52 00
    # reset printer
    q = Query()
    ip = db.get(q.data.mac == str(mac))['data']['ip']
    p = Network(ip, port=9100)
    # Open connection
    p.open()

    # Reset command
    p.text('\x1f\x1b\x1f\x27\x13\x14\x52\x00')

    # Close connection
    p.close()
