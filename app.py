import json
import os
import requests
from flask import Flask, request, jsonify, app, render_template
from flask_cors import CORS
from printer import print_base64, scan, is_online, connect_to_wifi
from time import sleep
import socket
import pickledb
import sys, signal

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://dev.vitalize.dev", "http://127.0.0.1:80"]}})
db = pickledb.load('./data.db', False)
meta = pickledb.load('./meta.db', False)
wifi = pickledb.load('./wifi.db', False)


@app.route("/status", methods=["GET"])
def check_status():
    res = []
    data = db.getall()
    for key in data:
        role = meta.get(key)['role'] if meta.get(key) and ('role' in meta.get(key).keys()) else "None"
        typ = meta.get(key)['type'] if meta.get(key) and ('type' in meta.get(key).keys()) else "None"
        res.append({f'{key}': {'ip': db.get(key),
                               'is_online': is_online(db.get(key), '9100') if db.get(key) != 'None' else "None",
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


@app.route("/connect_wifi/<mac>", methods=["POST"])
def connect_wifi(mac):
    if not db.get(mac):
        return app.response_class("Mac address not found", 404)
    connect_to_wifi(mac, wifi, db)
    return "successfully."


@app.route("/scan", methods=["POST"])
def scan_printer():
    res = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    rng = ".".join(s.getsockname()[0].split(".")[:3])
    s.close()
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
    image_path = os.path.join("./", image_file.filename)
    image_file.save(image_path)
    image_file.close()
    try:
        res = print_base64(image_path)
        if res:
            return {'success': True}
        else:
            return {'success': False}
    except Exception as e:
        print(e)
        return {'success': False}


@app.route('/update-project', methods=['POST'])
def update_project():
    # Update/install packages
    # reload flask

    os.system('pip install --upgrade pip')
    os.system('pip install -r requirements.txt')

    # Fetch latest code from GitHub
    repo_url = 'https://github.com/F4RAN/qutline-printer.git'
    os.system(f'git pull {repo_url}')

    # Restart app
    os.kill(os.getpid(), signal.SIGINT)
    #
    return jsonify({'message': 'Project updated successfully'})


@app.route('/setup', methods=['GET'])
def setup():
    with open('static/setup.html', 'r') as f:
        return f.read()


# @app.route("/print/cut", methods=["POST"])
# def cut_receipt():
#     try:
#         res = requests.get(f"http://192.168.1.100/?cutpaper")
#         if res.json() and res.json()['success']:
#             return {'success': True}
#         else:
#             return {'success': False}
#
#     except Exception as e:
#         print(e)
#         return {'success': False, 'message': 'Printer Connection Failed with cut paper request'}
#
#
# @app.route("/check_printer", methods=["GET"])
# def check_printer():
#     printer_config = open('printer.json')
#     config = json.loads(printer_config.read())
#     ip = config['ip']
#     port = config['port']
#     try:
#         res = requests.get("http://" + ip + ":" + str(port) + '/?selftest')
#         if res.json() and res.json()['success']:
#             return {'success': True}
#         else:
#             return {'success': False}
#     except Exception as e:
#         print(e)
#         return {'success': False, 'message':'Printer Connection Failed with self test request'}
#
#
# @app.route("/find_printer", methods=["GET"])
# def find_printer():
#     # Scan Network for printer
#     return "True"


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
