import os
import random
import subprocess
import uuid
from time import sleep
import requests
from flask import Flask, request, jsonify, app
from flask_cors import CORS
from configs.init import defaults
from configs.define_printer import Printer
from helpers.network import get_private_ip
from helpers.printer import scan, is_online, connect_to_wifi, hard_reset_printer, set_printer_ip_dynamic, set_printer_ip_static, set_lan_dhcp
from tinydb import TinyDB, where, Query
from helpers.lock_empty import run, lock
from configs.init import init_db, defaults
run()
from threading import Thread
# Start print handler thread
import sqlite3
init_db()

DATABASE = "dbs/database.sqlite"

app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["https://qdev-store.vitalize.dev", "https://uats.qutline.com",
                "https://store.qutline.com", "https://owner.qutline.com",
                "http://127.0.0.1:*", "http://localhost:3000", "http://localhost:*"]}})




def get_printers(cursor, select=[], where=[]):
    cursor.execute(f"SELECT {'*' if len(select) == 0 else ', '.join(select)} FROM Printer {'WHERE ' + ' AND '.join(where) if len(where) > 0 else ''}")
    printers = [dict(row) for row in cursor.fetchall()]
    return printers


@app.route("/change_dhcp/<mac>", methods=["PUT"])
def change_dhcp(mac):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor, ['mac_addr', 'ip_addr' ,'id', 'is_static_ip','connection'], [f"mac_addr = '{mac}'"])
    if len(printers) == 0:
        return app.response_class("Printer with this mac not found.")
    printer = printers[0]
    # Wifi
    if printer['connection'] == 1:
        if not printer['is_static_ip']:
            res = set_printer_ip_static(printer['ip_addr'])
            if not res:
                return app.response_class("Problem occured", 400)
            cursor.execute(f"UPDATE Printer SET is_static_ip = 1 WHERE mac_addr = '{mac}'")
            conn.commit()
            conn.close()
            print("Static for wifi")
        elif printer['is_static_ip']:
            res = set_printer_ip_dynamic(printer['ip_addr'])
            if not res:
                return app.response_class("Problem occured", 400)
            cursor.execute(f"UPDATE Printer SET is_static_ip = 0 WHERE mac_addr = '{mac}'")
            conn.commit()
            conn.close()
            print("Dynamic for wifi")
    # LAN
    if printer['connection'] == 0:
        if not printer['is_static_ip']:
            res = set_lan_dhcp(printer['ip_addr'],typ='static')
            if not res:
                    return app.response_class("Problem occured", 400)
            cursor.execute(f"UPDATE Printer SET is_static_ip = 1 WHERE mac_addr = '{mac}'")
            conn.commit()
            conn.close()
            print("Static for lan")
        elif printer['is_static_ip']:
            res = set_lan_dhcp(printer['ip_addr'],typ='dynamic')
            if not res:
                    return app.response_class("Problem occured", 400)
            cursor.execute(f"UPDATE Printer SET is_static_ip = 1 WHERE mac_addr = '{mac}'")
            conn.commit()
            conn.close()
            print("Dynamic for lan")
        
    
    return "Printer DHCP changed successfully."

# MIGRATED TO SQLITE
@app.route("/delete_default/<mac>/<typ>", methods=["DELETE"])
def delete_default(mac,typ):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor, ['mac_addr','id'], [f"mac_addr = '{mac}'"])
    if len(printers) == 0:
        return app.response_class("Printer with this mac not found.")
    printer = printers[0]
    # check job exists
    t = {
        "orders": 0,
        "receipts": 1,
        "tables": 2
    }
    print(t[typ], typ, printer['id'])
    job = cursor.execute(f"SELECT * FROM Job WHERE printer_id = {printer['id']} AND type = '{t[typ]}'").fetchone()
    if not job:
        return app.response_class("Job with this type not found", 404)
    
    cursor.execute(f"DELETE FROM Job WHERE printer_id = {printer['id']} AND type = '{t[typ]}'")
    conn.commit()
    return "Default printer removed successfully."

# MIGRATED TO SQLITE
@app.route("/set_default/<mac>", methods=["POST"])
def set_default(mac):
    req = request.json
    if req['type'] not in defaults:
        return app.response_class("Type not found", 404)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # type: 0: Orders, 1: Receipts, 2: Tables
    # convert req['type'] to int
    t = {
        "orders": 0,
        "receipts": 1,
        "tables": 2
    }

    jobs = cursor.execute(f"SELECT * FROM Job").fetchall()
    print(jobs,[job['type'] for job in jobs], req['type'], t[req['type']])
    if t[req['type']] in [job['type'] for job in jobs]:
        return app.response_class("This printer assigned for this job before", 400)
    else:
        # check printer exists
        printer = cursor.execute(f"SELECT * FROM Printer WHERE mac_addr = '{mac}'").fetchone()
        if not printer:
            return app.response_class("Printer with this mac not found", 404)
        cursor.execute(f"INSERT INTO Job (printer_id, type) VALUES ((SELECT id FROM Printer WHERE mac_addr = '{mac}'), '{t[req['type']]}')")
        conn.commit()
    conn.close()


    return "Default printer set successfully."

# MIGRATED TO SQLITE
@app.route("/get_defaults", methods=["GET"])
def get_default_options():
    return defaults


# MIGRATED TO SQLITE
@app.route("/status", methods=["GET"])
def check_status():
    res = []
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor)
    t = {
        0: "orders",
        1: "receipts",
        2: "tables"
    }
    for printer in printers:
        cursor.execute(f"SELECT type FROM Job WHERE printer_id = {printer['id']}")
        jobs = [t[j['type']] for j in cursor.fetchall()]
        res.append({'name': printer['name'], 'mac': printer['mac_addr'],
                    'ip': printer['ip_addr'], 'is_static_ip': printer['is_static_ip'],
                    'access': printer['access_level'], 'type': 'wifi' if printer['connection'] == 1 else 'lan',
                    'is_online': is_online(printer['ip_addr'], "9100"),
                    'defualt_for': jobs
                    })
    wifi = cursor.execute("SELECT * FROM WifiCredential").fetchone()
    if not wifi:
        wifi = {'ssid': '', 'password': ''}
    conn.close()
    
    return jsonify({'types': defaults, 'wifi': {'SSID': wifi['ssid'], 'PASSWORD': wifi['password']},
                    'printers': res})

# MIGRATED TO SQLITE
@app.route("/set_wifi", methods=["PUT"])
def set_wifi():
    req = request.json
    if not req['SSID'] or not req['PASSWORD']:
        return app.response_class("SSID or PASSWORD is not exists", 400)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("DELETE FROM WifiCredential")
    cursor.execute("INSERT INTO WifiCredential (ssid, password) VALUES (?, ?)", (req['SSID'], req['PASSWORD']))
    conn.commit()
    conn.close()

    return "Wi-fi credentials set successfully."

# MIGRATED TO SQLITE
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


# MIGRATED TO SQLITE
@app.route("/add_printer", methods=["POST"])
def add_printer():
    req = request.json
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor)
    macs = [printer['mac_addr'] for printer in printers]
    names = [printer['name'] for printer in printers]
    if not req['mac'] or not req['ip']:
        return app.response_class("Mac address or IP is not exists", 400)
    if req['mac'] in macs:
        return app.response_class("Mac address already exists", 400)
    # check role is exists
    if not req['name'] or req['name'] in names:
        return app.response_class("Name already exists", 400)
    # db.insert({'type': 'printer', 'data': {'name': req['name'], 'mac': req['mac'], 'ip': req['ip'],
    #                                        'access': 'admin', 'type': req['type']}})
    typ = 1 if req['type'] == 'wifi' else 0
    try:
        cursor.execute("INSERT INTO Printer (name, mac_addr, ip_addr, access_level, connection) VALUES (?, ?, ?, ?, ?)",
                       (req['name'], req['mac'], req['ip'], 0, typ))
        conn.commit()
        conn.close()
        return "Printer added successfully."
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return app.response_class(f"An error occurred: {str(e)}", 500)
    return "Printer added successfully."

# MIGRATED TO SQLITE
@app.route("/edit_printer/<mac>", methods=["PUT"])
def edit_printer(mac):
    req = request.json
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor)
    macs = [printer['mac_addr'] for printer in printers]
    if not mac in macs:
        return app.response_class("Mac address not found", 404)
    if not req['ip']:
        return app.response_class("IP is not exists", 400)
    q = Query()
    cursor.execute(f"SELECT * FROM Printer WHERE mac_addr = '{mac}'")
    printer = cursor.fetchone()
    # Update the fields
    update_fields = []
    
    if req.get('ip'):
        update_fields.append(f"ip_addr = '{req['ip']}'")
    
    if req.get('name'):
        update_fields.append(f"name = '{req['name']}'")
    
    if update_fields:
        update_query = f"UPDATE Printer SET {', '.join(update_fields)} WHERE mac_addr = '{mac}'"
        cursor.execute(update_query)
        conn.commit()


    return "Printer edited successfully."

# MIGRATED TO SQLITE
@app.route("/delete_printer/<mac>", methods=["DELETE"])
def delete_printer(mac):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor, ['mac_addr','id'], [f"mac_addr = '{mac}'"])
    if len(printers) == 0:
        return app.response_class("Printer with this mac not found.", 404)
    
    printer = printers[0]
    print(printer['id'],mac,printer['mac_addr'])
    # Remove relations in Job Table
    cursor.execute(f"DELETE FROM Job WHERE printer_id = {printer['id']}")
    # Remove from sqlite
    cursor.execute(f"DELETE FROM Printer WHERE mac_addr = '{mac}'")
    
    conn.commit()
    conn.close()
    
    return "Printer and all relations removed successfully."

# HERE
@app.route("/connect_wifi/<mac>", methods=["POST"])
def connect_wifi(mac):
    # if not db.get(mac):
    #     return app.response_class("Mac address not found", 404)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    printers = get_printers(cursor, ['mac_addr','id','name'], [f"mac_addr = '{mac}'"])
    if len(printers) == 0:
        return app.response_class("Printer with this mac not found.")
    printer = cursor.execute(f"SELECT ip_addr, name FROM Printer WHERE mac_addr = '{mac}'").fetchone()
    ip = printer['ip_addr']
    name = printer['name']
    credential = cursor.execute("SELECT * FROM WifiCredential").fetchone()
    wifi = {'ssid': credential['ssid'], 'password': credential['password']}
    name = connect_to_wifi(ip, mac, wifi, name)
    conn.close()
    return app.response_class(name, 200)


@app.route("/scan", methods=["POST"])
def scan_printer():
    setup = False
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    q = request.args.get('setup')
    if q == '1':
        setup = True

    private_ip = get_private_ip()
    rng = ".".join(private_ip.split(".")[:3])
    data = scan(rng, setup, cursor)
    conn.commit()
    conn.close()
    return jsonify(data)

def verify_printer(prt):
    lc = 0
    while lock.locked():
        lc += 1
        sleep(1)
        if lc > 10:
            return False, app.response_class("Maintain mode please wait", 400)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    types = cursor.execute("SELECT type FROM Job").fetchall()
    t1 = {
        0: "orders",
        1: "receipts",
        2: "tables"
    }
    default_printers_types = [t1[ty['type']] for ty in types]
    
    if prt not in default_printers_types:
        return False, app.response_class("Printer part not founds", 404)
    try:
        t2 = {
            "orders": 0,
            "receipts": 1,
            "tables": 2
        }
        addrs = cursor.execute(f"SELECT mac_addr, ip_addr FROM Printer WHERE id = (SELECT printer_id FROM Job WHERE type = '{t2[prt]}')").fetchone()
        mac, ip = addrs['mac_addr'], addrs['ip_addr']
    except Exception as e:
            
        return False, app.response_class("Printer part not found", 404)
    if not ip:
        return False, app.response_class("IP part not found", 404)
    return {'mac':mac,'ip':ip}, False

@app.route("/print_code/<prt>", methods=["POST"])
def print_code(prt):
    req = request.json
    info, err = verify_printer(prt)
    if not info:
        return err
    ip = info['ip']
    mac = info['mac']
    try:
        printer = Printer(mac)
        res = printer.print(image_path="",ip=ip,tp="code",code=req['code'],name=req['name'])
        if res:
            return {'success': True}
        else:
            return app.response_class("Printer connection problem, go to the Dashboard > Settings > Connected "
                                      "Devices, and make sure information is true", 400)
    except Exception as e:
        print(e)
        return {'success': False}

@app.route("/print/<prt>", methods=["POST"])
def print_receipt(prt):
    info, err = verify_printer(prt)
    if not info:
        return err
    ip = info['ip']
    mac = info['mac']

    if 'imageFile' not in request.files:
        return app.response_class("No image file selected", 400)

    image_file = request.files['imageFile']

    if image_file.filename == '':
        return app.response_class("No image name selected", 400)

    # Save the image file to a desired location

    image_path = os.path.join("./images/", str(uuid.uuid4()) + image_file.filename)
    with open(image_path, "wb") as f:
        f.write(image_file.read())
        f.flush()
        os.fsync(f.fileno())
    try:
        printer = Printer(mac)
        res = printer.print(image_path, ip)
        if res:
            return {'success': True}
        else:
            return app.response_class("Printer connection problem, go to the Dashboard > Settings > Connected "
                                      "Devices, and make sure information is true", 400)
    except Exception as e:
        print(e)
        return {'success': False}


@app.route("/check_update", methods=["GET"])
def check_update():
    # Read VERSION file
    with open('VERSION', 'r') as f:
        in_version = f.read().strip()
    res = requests.get('https://raw.githubusercontent.com/F4RAN/qutline-printer/main/VERSION')
    out_version = res.text.strip()
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
    cwd = os.getcwd()
    script_path = os.path.join(cwd, "setup/update.sh")
    sb = subprocess.Popen(['/bin/bash', script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print(mac)
        printers = get_printers(cursor, ['mac_addr','ip_addr'], [f"mac_addr = '{mac}'"])
        printer = printers[0]
        if not printer:
            return app.response_class("Printer with this mac not found", 404)
        hard_reset_printer(printer['ip_addr'], mac)
        return jsonify({'message': 'Printer reset successfully'})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Printer reset failed'})


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
