import os
import subprocess
import uuid
from time import sleep
import requests
from flask import Flask, request, jsonify, app
from flask_cors import CORS

from configs.init import defaults
from helpers.network import get_private_ip
from helpers.printer import print_base64, scan, is_online, connect_to_wifi,print_handler, hard_reset_printer
from tinydb import TinyDB, where, Query
from threading import Thread
# Start print handler thread
t = Thread(target=print_handler)
t.daemon = True
t.start()

db = TinyDB('dbs/db.json')

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["https://dev.vitalize.dev", "http://127.0.0.1:*", "http://localhost:3000", "http://localhost:*"]}})

@app.route("/delete_default/<mac>/<typ>", methods=["DELETE"])
def delete_default(mac,typ):
    stores = db.search(where('type') == 'store')
    if len(stores) < 1:
        return app.response_class("Default printer not found", 404)
    else:
        for store in stores:
            for i, dfp in enumerate(store['data']):
                if dfp['printer'] == mac and dfp['type'] == typ:
                    del store['data'][i]
                    db.update(store, where('type') == 'store')
                    return "Default printer deleted successfully."
    return app.response_class("Default printer not found", 404)


@app.route("/set_default/<mac>", methods=["POST"])
def set_default(mac):
    req = request.json
    if req['type'] not in defaults:
        return app.response_class("Type not found", 404)
    printers = db.search(where('type') == 'printer')
    macs = [printer['data']['mac'] for printer in printers]
    if not mac in macs:
        return app.response_class("Mac address not found", 404)
    stores = db.search(where('type') == 'store')
    if len(stores) < 1:
        db.insert({'type': 'store', 'data': [{'type': req['type'], 'printer': mac}]})
    else:
        for store in stores:
            if store['data'][0]['type'] == req['type']:
                store['data'][0]['printer'] = mac
                db.update(store, where('type') == 'store')
                print("here")
            elif req['type'] not in [dfp['type'] for dfp in store['data']]:
                print("here2")
                store['data'].append({'type': req['type'], 'printer': mac})
                db.update(store, where('type') == 'store')
    return "Default printer set successfully."


@app.route("/get_defaults", methods=["GET"])
def get_default_options():
    return defaults



@app.route("/status", methods=["GET"])
def check_status():
    res = []
    printers = db.search(where('type') == 'printer')
    default_printers = [st_part['data'] for st_part in db.search(where('type') == 'store')]
    default_printers_types = [dfp['type'] for dfp in default_printers[0]]
    default_pritner_macs = [dfp['printer'] for dfp in default_printers[0]]
    for printer in printers:
        defs = []
        for p in default_printers[0]:
            if p['printer'] == printer['data']['mac']:
                defs.append(p['type'])

        res.append({'name': printer['data']['name'], 'mac': printer['data']['mac'],
                    'ip': printer['data']['ip'],
                    'access': printer['data']['access'], 'type': printer['data']['type'],
                    'is_online': is_online(printer['data']['ip'], "9100"),
                    'defualt_for': defs
                    })
    wifi = db.search(where('type') == 'credential')[0]['data']

    return jsonify({'types': default_printers_types, 'wifi': {'SSID': wifi['ssid'], 'PASSWORD': wifi['password']},
                    'printers': res})


@app.route("/set_wifi", methods=["PUT"])
def set_wifi():
    req = request.json
    if not req['SSID'] or not req['PASSWORD']:
        return app.response_class("SSID or PASSWORD is not exists", 400)
    wifi = db.search(where('type') == 'credential')[0]['data']
    if wifi:
        new_wifi = {'ssid': req['SSID'], 'password': req['PASSWORD']}
        db.update({'type': 'credential', 'data': new_wifi}, where('type') == 'credential')
    else:
        new_wifi = {'ssid': req['SSID'], 'password': req['PASSWORD']}
        db.update({'type': 'credential', 'data': new_wifi}, where('type') == 'credential')

    return "Wi-fi credentials set successfully."


@app.route("/get_wifi", methods=["GET"])
def get_wifi():
    # Check wifi name in termux
    ssid = ""
    try:
        ssid = subprocess.check_output(['termux-wifi-connectioninfo']).decode('utf-8').split('"ssid": "')[1].split('"')[
            0]
    except:
        pass

    return jsonify({'ssid': ssid})


@app.route("/add_printer", methods=["POST"])
def add_printer():
    req = request.json
    printers = db.search(where('type') == 'printer')
    macs = [printer['data']['mac'] for printer in printers]
    names = [printer['data']['name'] for printer in printers]
    if not req['mac'] or not req['ip']:
        return app.response_class("Mac address or IP is not exists", 400)
    if req['mac'] in macs:
        return app.response_class("Mac address already exists", 400)
    # check role is exists
    if not req['name'] or req['name'] in names:
        return app.response_class("Name already exists", 400)
    db.insert({'type': 'printer', 'data': {'name': req['name'], 'mac': req['mac'], 'ip': req['ip'],
                                           'access': 'admin', 'type': req['type']}})
    return "Printer added successfully."


@app.route("/edit_printer/<mac>", methods=["PUT"])
def edit_printer(mac):
    req = request.json
    macs = [printer['data']['mac'] for printer in db.search(where('type') == 'printer')]
    if not mac in macs:
        return app.response_class("Mac address not found", 404)
    if not req['ip']:
        return app.response_class("IP is not exists", 400)
    q = Query()
    printer = db.get(q.data.mac == str(mac))
    printer['data'].update({'ip': req['ip']})
    printer['data'].update({'name': req['name']})
    db.update(printer, q.data.mac == str(mac))


    return "Printer edited successfully."


@app.route("/delete_printer/<mac>", methods=["DELETE"])
def delete_printer(mac):
    macs = [printer['data']['mac'] for printer in db.search(where('type') == 'printer')]
    if not mac in macs:
        return app.response_class("Mac address not found", 404)

    q = Query()
    db.remove(q.data.mac == str(mac))
    # delete from defaults too if exists
    default_printers = [st_part['data'] for st_part in db.search(where('type') == 'store')]
    default_pritner_macs = [dfp['printer'] for dfp in default_printers[0]]
    defs = []
    updating = default_printers[0]
    for p in default_printers[0]:
        if p['printer'] == mac:
            updating.pop(default_pritner_macs.index(mac))
            default_pritner_macs.pop(default_pritner_macs.index(mac))
            db.update({'type': 'store', 'data': updating}, where('type') == 'store')


    return "Printer removed successfully."


@app.route("/connect_wifi/<mac>", methods=["POST"])
def connect_wifi(mac):
    if not db.get(mac):
        return app.response_class("Mac address not found", 404)
    credential = db.search(where('type') == 'credential')[0]['data']
    wifi = {'ssid': credential['ssid'], 'password': credential['password']}
    connect_to_wifi(mac, wifi)
    return "Device connected to Wi-Fi successfully."


@app.route("/scan", methods=["POST"])
def scan_printer():
    setup = False
    q = request.args.get('setup')
    if q == '1':
        setup = True

    private_ip = get_private_ip()
    rng = ".".join(private_ip.split(".")[:3])
    data = scan(rng, setup)

    return jsonify(data)


@app.route("/print/<prt>", methods=["POST"])
def print_receipt(prt):
    default_printers = [st_part['data'] for st_part in db.search(where('type') == 'store')]
    default_printers_types = [dfp['type'] for dfp in default_printers[0]]
    if prt not in default_printers_types:
        return app.response_class("Printer part not founds", 404)
    try:
        ip = ""
        mac = default_printers[0][default_printers_types.index(prt)]['printer']
        printers = db.search(where('type') == 'printer')
        for p in printers:
            if p['data']['mac'] == mac:
                ip = p['data']['ip']
    except Exception as e:
        print(e)
        return app.response_class("Printer part not found", 404)
    if not ip:
        return app.response_class("IP part not found", 404)

    if 'imageFile' not in request.files:
        return jsonify({'success': False, 'message': 'No image file found'})

    image_file = request.files['imageFile']

    if image_file.filename == '':
        return jsonify({'success': False, 'message': 'No image file selected'})

    # Save the image file to a desired location

    image_path = os.path.join("./images/", str(uuid.uuid4()) + image_file.filename)
    with open(image_path, "wb") as f:
        f.write(image_file.read())
        f.flush()
        os.fsync(f.fileno())
    try:
        res = print_base64(image_path, ip)
        if res:
            return {'success': True}
        else:
            return {'success': False}
    except Exception as e:
        print(e)
        return {'success': False}


@app.route("/check_update", methods=["GET"])
def check_update():
    # Read VERSION file
    with open('VERSION', 'r') as f:
        in_version = f.read()
    res = requests.get('https://raw.githubusercontent.com/F4RAN/qutline-printer/main/VERSION')
    out_version = res.text
    if in_version == out_version:
        return jsonify({'update': False})
    else:
        return jsonify({'update': True, 'version': out_version})


@app.route('/update_project', methods=['POST'])
def update_project():
    repo_url = 'https://github.com/F4RAN/qutline-printer.git'
    os.system(f'git pull {repo_url}')
    sleep(5)
    # update termux
    timer = 0
    sb = subprocess.Popen(['./setup/update.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while sb.poll() is None:
        print(str(sb.stdout.readline()))
        sleep(1)
        timer += 1
        if timer > 600:
            return jsonify({'message': 'Update failed'})

    subprocess.Popen(["python3", "restart.py"])
    return jsonify({'message': 'Server restarting'})


@app.route('/setup', methods=['GET'])
def setup():
    with open('ui/setup.html', 'r') as f:
        return f.read()


@app.route('/hard_reset/<mac>', methods=['POST'])
def hard_reset(mac):
    try:
        hard_reset_printer(mac)
        return jsonify({'message': 'Printer reset successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Printer reset failed'})


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
