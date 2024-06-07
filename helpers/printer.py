import threading
from time import sleep
from escpos.printer import Network
import subprocess
import re
import requests
import socket
from tinydb import TinyDB, Query, where
from slugify import slugify

tout = 20


def get_printers(cursor, select=[], where=[]):
    cursor.execute(
        f"SELECT {'*' if len(select) == 0 else ', '.join(select)} FROM Printer {'WHERE ' + ' AND '.join(where) if len(where) > 0 else ''}")
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
            max_num = 0
            for printer in printers:
                if printer['name'].find("Printer #"):
                    max_num = max(max_num, int(printer['name'].split("#")[1]))
            name = f"Printer #{max_num + 1}"
            # check mac address exists
            check = get_printers(cursor, where=[f"mac_addr = '{mac}'"])
            if len(check) != 0:
                cursor.execute(f"UPDATE Printer SET ip_addr = '{ip}' WHERE mac_addr = '{mac}'")
            else:
                cursor.execute(
                    f"INSERT INTO Printer (name, connection, mac_addr, ip_addr, access_level, is_static_ip) VALUES ('{name}', 1, '{mac}', '{ip}', 0, 1)")

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
                    max_num = 0
                    for printer in printers:
                        if printer['name'].find("Printer #"):
                            max_num = max(max_num, int(printer['name'].split("#")[1]))
                    name = f"Printer #{max_num + 1}"
                    check = get_printers(cursor, where=[f"mac_addr = '{mac}'"])
                    if len(check) != 0:
                        cursor.execute(f"UPDATE Printer SET ip_addr = '{ip}', connection = 0 WHERE mac_addr = '{mac}'")
                    else:
                        cursor.execute(
                            f"INSERT INTO Printer (name, connection, mac_addr, ip_addr, access_level, is_static_ip) VALUES ('{name}', 0, '{mac}', '{ip}', 0, 0)")

                    conflict_printers = get_printers(cursor, select=['mac_addr', 'ip_addr', 'name'],
                                                     where=[f"ip_addr = '{ip}'"])

                    for p in conflict_printers:
                        if p['mac_addr'] != mac and p['ip_addr'] == ip:
                            # set None instead of ip
                            cursor.execute(f"UPDATE Printer SET ip_addr = 'None' WHERE mac_addr = '{p['mac_addr']}'")


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


def save_changes(ip, headers):
    res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                         timeout=tout)


def rename_wifi(ip, name):
    sleep(5)
    print("starting rename")
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wirepoint_en.html',
    }
    try:
        payload = f'ap_setting_ssid={slugify(name)}'
        print("Name changed", payload)
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
    except Exception as e:
        print("inside error", e)
        name = "Unknown Printer"
    save_changes(ip, headers)
    print("starting after rename")


def connect_to_wifi(ip, mac, wifi, name):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wireless_en.html',

    }
    ssid = wifi["ssid"]
    password = wifi["password"]
    payload = f'sta_setting_encry=AES&sta_setting_auth=WPA2PSK&sta_setting_ssid={ssid}&sta_setting_auth_sel=WPA2PSK&sta_setting_encry_sel=AES&sta_setting_type_sel=ASCII&sta_setting_wpakey={password}&wan_setting_dhcp=STATIC'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
    except Exception as e:
        print(e)
        print("HTTP request to printer to set wifi credentials failed.")
        name = "Unknown Printer"
    threading.Thread(target=rename_wifi, args=(ip, name,)).start()
    # Save changes and restart after rename wifi


def set_printer_ip_static(ip):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wireless_en.html',
    }
    res = requests.get("http://" + ip + '/wireless_en.html', headers=headers, timeout=tout)
    pattern = r'var\s+(\w+)\s*=\s*"([^"]+)"'
    matches = re.findall(pattern, str(res.content))
    result = dict(matches)
    payload = f'wan_setting_dhcp=STATIC&sta_setting_encry={result["sta_setting_encry"]}&sta_setting_auth={result["sta_setting_auth"]}&sta_setting_ssid={result["sta_setting_ssid"]}&sta_setting_auth_sel={result["sta_setting_auth"]}&sta_setting_encry_sel={result["sta_setting_encry"]}&sta_setting_type_sel=ASCII&sta_setting_wpakey={result["sta_setting_wpakey"]}&wan_setting_ip={result["wan_setting_ip"]}&wan_setting_msk={result["wan_setting_msk"]}&wan_setting_gw={result["wan_setting_gw"]}&wan_setting_dns={result["wan_setting_dns"]}'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                             timeout=tout)
        print("Successfully set to static")
        return True
    except Exception as e:
        print(e)
    return False


def set_printer_ip_dynamic(ip):
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wireless_en.html',
    }
    res = requests.get("http://" + ip + '/wireless_en.html', headers=headers, timeout=tout)
    pattern = r'var\s+(\w+)\s*=\s*"([^"]+)"'
    matches = re.findall(pattern, str(res.content))
    result = dict(matches)
    payload = f'wan_setting_dhcp=DHCP&sta_setting_encry={result["sta_setting_encry"]}&sta_setting_auth={result["sta_setting_auth"]}&sta_setting_ssid={result["sta_setting_ssid"]}&sta_setting_auth_sel={result["sta_setting_auth"]}&sta_setting_encry_sel={result["sta_setting_encry"]}&sta_setting_type_sel=ASCII&sta_setting_wpakey={result["sta_setting_wpakey"]}'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                             timeout=tout)
        print("Successfully set to dhcp")
        return True
    except Exception as e:
        print(e)
        return False
    return False


def set_lan_dhcp(ip, typ):
    socket.setdefaulttimeout(5)
    response = socket.socket()
    response.connect((ip, 80))

    request = f"GET /ip_config.htm HTTP/1.1\r\nHost: {ip}\r\n\r\n"
    response.send(request.encode('utf-8'))

    html = b""
    try:
        while True:
            data = response.recv(1024)
            if not data:
                break
            html += data
    except:
        pass
    try:
        response.shutdown(socket.SHUT_RD)
        response.close()
    except:
        print("Problem with closing socket")

    # Extract dhcp_mode

    dhcp_mode = re.search(r'type=radio\s+CHECKED\s+value=(\d+)\s+name=dhcp\_mode', html.decode('latin-1')).group(1)

    # Extract DHCP_time
    dhcp_time = re.search(r'value=(\d+).*?name=DHCP\_time', html.decode('latin-1')).group(1)

    # Extract IP address
    ip_address = re.findall(r'value=(\d+).*?name=IP\_(\d+)', html.decode('latin-1'))
    ip1, ip2, ip3, ip4 = [value for _, value in ip_address]

    # Extract subnet mask
    subnet_mask = re.findall(r'value=(\d+).*?name=MASK\_(\d+)', html.decode('latin-1'))
    mask1, mask2, mask3, mask4 = [value for _, value in subnet_mask]

    # Extract gateway address
    gateway = re.findall(r'value=(\d+).*?name=GW\_IP\_(\d+)', html.decode('latin-1'))
    gw1, gw2, gw3, gw4 = [value for _, value in gateway]

    # Construct the query string
    if typ == 'static':
        query = f"dhcp_mode=0&IP_1={ip1}&IP_2={ip2}&IP_3={ip3}&IP_4={ip4}&MASK_1={mask1}&MASK_2={mask2}&MASK_3={mask3}&MASK_4={mask4}&GW_IP_1={gw1}&GW_IP_2={gw2}&GW_IP_3={gw3}&GW_IP_4={gw4}&__use_dhcp=0&save=+Save+"

    elif typ == 'dynamic':
        query = f"dhcp_mode=1&DHCP_time={dhcp_time}&__use_dhcp=0&save=+Save+"

    socket.setdefaulttimeout(5)
    response = socket.socket()
    response.connect((ip, 80))

    request = f"GET /ip_config.htm?{query} HTTP/1.1\r\nHost: {ip}\r\n\r"
    response.send(request.encode('utf-8'))

    html = b""
    try:
        while True:
            data = response.recv(1024)
            if not data:
                break
            html += data
    except:
        pass

    try:
        response.shutdown(socket.SHUT_RD)
        response.close()
    except:
        return False
        print("Problem with closing socket")
    return True


def hard_reset_printer(ip, mac):
    # Command : 1f 1b 1f 27 13 14 52 00
    # reset printer
    print("here in hard reset")
    ip = ip
    p = Network(ip, port=9100)
    # Open connection
    p.open()

    # Reset command
    p.text('\x1f\x1b\x1f\x27\x13\x14\x52\x00')

    # Close connection
    p.close()
