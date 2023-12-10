import os
import subprocess
import uuid
from threading import Thread
from time import sleep
from datetime import datetime
import requests
from flask import Flask, request, jsonify, app
from flask_cors import CORS
from helpers.network import get_private_ip
from helpers.printer import print_base64, scan, is_online, connect_to_wifi, print_handler, hard_reset_printer
import pickledb

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["https://dev.vitalize.dev", "http://127.0.0.1:*", "http://localhost:3000", "http://localhost:*"]}})
db = pickledb.load('./dbs/data.db', False)
meta = pickledb.load('./dbs/meta.db', False)
wifi = pickledb.load('./dbs/wifi.db', False)
# Start print handler thread
t = Thread(target=print_handler)
t.daemon = True
t.start()


@app.route("/status", methods=["GET"])
def check_status():
    res = []
    data = db.getall()
    for key in data:
        role = meta.get(key)['role'] if meta.get(key) and ('role' in meta.get(key).keys()) else "None"
        typ = meta.get(key)['type'] if meta.get(key) and ('type' in meta.get(key).keys()) else "None"
        res.append({f'{key}': {'ip': db.get(key),
                               'is_online': is_online(db.get(key)) if db.get(key) != 'None' else "None",
                               'role': role, 'type': typ}})
    return jsonify({'wifi': {'SSID': wifi.get('SSID'), 'PASSWORD': wifi.get('PASSWORD')}, 'printers': res})


@app.route("/set_wifi", methods=["POST"])
def set_wifi():
    req = request.json
    if not req['SSID'] or not req['PASSWORD']:
        return app.response_class("SSID or PASSWORD is not exists", 400)
    wifi.set('SSID', req['SSID'])
    wifi.set('PASSWORD', req['PASSWORD'])
    wifi.dump()
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


@app.route("/add-printer", methods=["POST"])
def add_printer():
    req = request.json
    if not req['mac'] or not req['ip']:
        return app.response_class("Mac address or IP is not exists", 400)
    if db.get(req['mac']):
        return app.response_class("Mac address already exists", 400)
    if db.get(req['mac']):
        return app.response_class("Mac address already exists", 400)
    # check role is exists
    all_metas = meta.getall()
    for key in all_metas:
        mt = meta.get(key)
        if 'role' in mt and mt['role'] == req['role']:
            return app.response_class("Role already exists", 400)
    db.set(req['mac'], req['ip'])
    meta.set(req['mac'], {'role': req['role'], 'type': req['type']})
    db.dump()
    meta.dump()
    return "Printer added successfully."


@app.route("/edit-printer/<mac>", methods=["PUT"])
def edit_printer(mac):
    req = request.json
    if not db.get(mac):
        return app.response_class("Mac address not found", 404)
    if not req['ip']:
        return app.response_class("IP is not exists", 400)
    db.set(mac, req['ip'])
    if req['role']:
        obj = meta.get(mac)
        obj['role'] = req['role']
        meta.set(mac, obj)
        meta.dump()
    db.dump()
    return "Printer edited successfully."


@app.route("/connect_wifi/<mac>", methods=["POST"])
def connect_wifi(mac):
    if not db.get(mac):
        return app.response_class("Mac address not found", 404)
    connect_to_wifi(mac, wifi, db)
    return "successfully."


@app.route("/scan", methods=["POST"])
def scan_printer():
    res = []
    private_ip = get_private_ip()
    rng = ".".join(private_ip.split(".")[:3])
    data = scan(rng, db, meta)
    for key in data:
        res.append({f'{key}': db.get(key)})
    return jsonify(res)


@app.route("/print", methods=["POST"])
def print_receipt():
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
        res = print_base64(image_path, db)
        if res:
            return {'success': True}
        else:
            return {'success': False}
    except Exception as e:
        print(e)
        return {'success': False}


@app.route("/check-update", methods=["GET"])
def check_update():
    # Read VERSION file
    with open('VERSION', 'r') as f:
        in_version = f.read()
    res = requests.get('https://raw.githubusercontent.com/F4RAN/qutline-printer/main/VERSION')
    out_version = res.text
    print(in_version, out_version)
    if in_version == out_version:
        return jsonify({'update': False})
    else:
        return jsonify({'update': True, 'version': out_version})


@app.route('/update-project', methods=['POST'])
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
    with open('ui/setup2.html', 'r') as f:
        return f.read()


@app.route('/hard-reset/<mac>', methods=['POST'])
def hard_reset(mac):
    try:
        hard_reset_printer(mac, db)
        return jsonify({'message': 'Printer reset successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Printer reset failed'})


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
