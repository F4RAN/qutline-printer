import requests
import re
tout = 50
def get_printer_details():
    ip = "192.168.1.159"
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Origin': f'http://{ip}',
        'Referer': f'http://{ip}/wireless_en.html',
    }
    res = requests.get("http://" + ip + '/wireless_en.html', headers=headers, timeout=tout)
    # print(res.content)
    pattern = r'var\s+(\w+)\s*=\s*"([^"]+)"'
    matches = re.findall(pattern, str(res.content))
    result = dict(matches)
    print(result)
    payload = f'sta_setting_encry={result["sta_setting_encry"]}&sta_setting_auth={result["sta_setting_auth"]}&sta_setting_ssid={result["sta_setting_ssid"]}&sta_setting_auth_sel={result["sta_setting_auth_sel"]}&sta_setting_encry_sel={result["sta_setting_encry_sel"]}&sta_setting_type_sel={result["sta_setting_type_sel"]}&sta_setting_wpakey={result["sta_setting_wpakey"]}&wan_setting_dhcp={result["wan_setting_dhcp"]}&wan_setting_ip={result["wan_setting_ip"]}&wan_setting_msk={result["wan_setting_msk"]}&wan_setting_gw={result["wan_setting_gw"]}&wan_setting_dns={result["wan_setting_dns"]}'
    try:
        res = requests.post("http://" + ip + '/do_cmd_en.html', headers=headers, data=payload, timeout=tout)
        res2 = requests.post("http://" + ip + "/success_en.html", headers=headers, data='HF_PROCESS_CMD=RESTART',
                             timeout=tout)
    except Exception as e:
        print(e)


get_printer_details()