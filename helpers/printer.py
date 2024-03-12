from time import sleep
from escpos.printer import Network
import subprocess
import re
import requests
import socket
from tinydb import TinyDB, Query, where
tout = 20

def get_printers(cursor, select=[], where=[]):
    cursor.execute(f"SELECT {'*' if len(select) == 0 else ', '.join(select)} FROM Printer {'WHERE ' + ' AND '.join(where) if len(where) > 0 else ''}")
    printers = [dict(row) for row in cursor.fetchall()]
    return printers

def scan(rng, setup, cursor):
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
            printers = get_printers(cursor)
            max_num = 1
            for printer in printers:
                if printer['name'].find("Printer #"):
                    max_num = max(max_num, int(printer['name'].split("#")[1]))
            name = f"Printer #{max_num + 1}"
            cursor.execute(f"INSERT INTO Printer (name, connection, mac_addr, ip_addr, access_level) VALUES ('{name}', 1, '{mac}', '{ip}', 0)")
            cursor.commit()
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
                    printers = get_printers(cursor)
                    max_num = 1
                    for printer in printers:
                        if printer['name'].find("Printer #"):
                            max_num = max(max_num, int(printer['name'].split("#")[1]))
                    name = f"Printer #{max_num + 1}"
                    cursor.execute(f"INSERT INTO Printer (name, connection, mac_addr, ip_addr, access_level) VALUES ('{name}', 1, '{mac}', '{ip}', 0)")
                    cursor.commit()
                    conflict_printers = get_printers(cursor, select=['mac_addr', 'ip_addr', 'name'], where=[f"ip_addr = '{ip}'"])

                    for p in conflict_printers:
                        if p['mac_addr'] != mac and p['ip_addr'] == ip:
                            # set None instead of ip
                            cursor.execute(f"UPDATE Printer SET ip_addr = 'None' WHERE mac_addr = '{p['mac_addr']}'")
                            cursor.commit()

            except:
                print("Socket not found")

            else:
                print("MAC ADDR not found")

            pass

    result = []
    printers = get_printers(cursor)
    for printer in printers:
        if printer['ip_addr'] in founded_ips:
            result.append(dict(printer))
        elif not setup:
            result.append(dict(printer))
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

def connect_to_wifi(ip, mac, wifi):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wireless_en.html',

    }
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


def hard_reset_printer(ip, mac):
    # Command : 1f 1b 1f 27 13 14 52 00
    # reset printer
    ip = ip
    p = Network(ip, port=9100)
    # Open connection
    p.open()

    # Reset command
    p.text('\x1f\x1b\x1f\x27\x13\x14\x52\x00')

    # Close connection
    p.close()
