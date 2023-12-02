import multiprocessing
import os
import subprocess
from time import sleep

from flask import Flask, request, jsonify, app
from flask_cors import CORS
from helpers.printer import print_base64, scan, is_online, connect_to_wifi
import socket
import pickledb
import signal

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://dev.vitalize.dev", "http://127.0.0.1:*", "http://localhost:*"]}})
db = pickledb.load('./dbs/data.db', False)
meta = pickledb.load('./dbs/meta.db', False)
wifi = pickledb.load('./dbs/wifi.db', False)


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

    # update project
    # os.system('pip install --upgrade pip')
    # os.system('pip install -r requirements.txt')
    #
    # # Fetch latest code from GitHub
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

    multiprocessing.Process(target=restart_server, args=(os.getpid(),)).start()
    return jsonify({'message': 'Server restarting'})


def restart_server(main_pid):
    sleep(2)
    command = "pkill -f 'app.py'"

    process = subprocess.Popen(command, shell=True)
    process.wait()

    # Optionally, you can check the return code to see if the command was successful
    if process.returncode == 0:
        print("Command executed successfully.")
    else:
        print("Command failed.")
    # os.kill(main_pid, signal.SIGINT)
    while True:
        print('Trying to run again')
        sleep(5)
        try:
            os.system('python app.py')
            break
        except Exception as e:
            print(e)


@app.route('/setup', methods=['GET'])
def setup():
    with open('static/setup.html', 'r') as f:
        return f.read()


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)
