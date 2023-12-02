import base64
from io import BytesIO
from escpos.printer import Network
from PIL import Image
import subprocess
import re
import requests
import socket


def print_base64(image_path):
    try:  # Connect to the printer
        printer = Network("192.168.1.100", port=9100)  # Replace with your printer's IP address and port
        printer.set(align='center', width=2, height=2)
        printer.image(image_path)
        # Cut the paper
        printer.cut()
        return True
    except Exception as e:
        print(e)
        return False


founded_ips = []


def scan(rng, db, meta):
    print('rng is:', rng)
    nmap_args = f'nmap -p 9100 --open {rng}.* -T5 -M200  -oG -'
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

    for ip in founded_ips:
        headers = {
            # 'Authorization': 'Basic admin:admin'
            'Authorization': 'Basic YWRtaW46YWRtaW4='
        }
        try:
            print(ip)
            res = requests.get("http://" + ip + '/status_en.html', headers=headers)
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
            while True:
                data = response.recv(1024)
                if not data:
                    break
                html += data
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

            else:
                print("MAC ADDR not found")

            pass
    data = db.getall()
    print(data)
    for key in data:
        if db.get(key) not in founded_ips:
            print(db.get(key),"here in set none")
            db.set(key, "None")
            db.dump()
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
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART')

    except Exception as e:
        print(e)
        print("HTTP request to printer to set wifi credentials failed.")
        pass
