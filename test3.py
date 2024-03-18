import requests
import re
import socket
tout = 50
def set_printer_ip_static():
    ip = "192.168.1.159"
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
    except Exception as e:
        print(e)

def set_printer_ip_dynamic():
    ip = "192.168.1.159"
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
        print("Successfully set to static")
    except Exception as e:
        print(e)


def set_lan_dhcp(typ='static'):
    ip = "192.168.1.100"
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
        
    elif typ =='dynamic':
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
        print("Problem with closing socket")
    
    

set_lan_dhcp(typ="dynamic")
    