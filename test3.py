import requests
import re
import socket
tout = 50
def set_printer_ip_static():
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
    # payload = f'wan_setting_dhcp=DHCP&sta_setting_encry={result["sta_setting_encry"]}&sta_setting_auth={result["sta_setting_auth"]}&sta_setting_ssid={result["sta_setting_ssid"]}&sta_setting_auth_sel={result["sta_setting_auth"]}&sta_setting_encry_sel={result["sta_setting_encry"]}&sta_setting_type_sel=ASCII&sta_setting_wpakey={result["sta_setting_wpakey"]}'
    payload='sta_setting_encry=AES&sta_setting_auth=WPA2PSK&sta_setting_ssid=Verizon_ZL3BSF&sta_setting_auth_sel=WPA2PSK&sta_setting_encry_sel=AES&sta_setting_type_sel=ASCII&sta_setting_wpakey=merge9-bib-pert&wan_setting_dhcp=DHCP'
    print(payload)
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
    'Authorization': 'Basic YWRtaW46YWRtaW4=',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://192.168.1.155',
    'Referer': 'http://192.168.1.155/wireless_en.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        # res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
        #                      timeout=tout)
        print("Successfully set to dynamic")
    except Exception as e:
        print(e)


 

    

# set_lan_dhcp(typ="dynamic")

set_printer_ip_dynamic()