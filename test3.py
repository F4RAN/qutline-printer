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
    ip = "192.168.1.155"
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



    

# set_lan_dhcp(typ="dynamic")

set_printer_ip_dynamic()