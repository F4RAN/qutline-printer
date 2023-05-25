import json
import os
import requests
from flask import Flask, request
from flask_cors import CORS
from printer import print_base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://dev.vitalize.dev", "192.168.1.100:80"]}})


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
    image_file.flush()
    try:
        res = print_base64(image_path)
        if res:
            return {'success': True}
        else:
            return {'success': False}
    except Exception as e:
        print(e)
        return {'success': False}


@app.route("/print/cut", methods=["POST"])
def cut_receipt():
    try:
        res = requests.get(f"http://192.168.1.100/?cutpaper")
        if res.json() and res.json()['success']:
            return {'success': True}
        else:
            return {'success': False}

    except Exception as e:
        print(e)
        return {'success': False, 'message': 'Printer Connection Failed with cut paper request'}


@app.route("/check_printer", methods=["GET"])
def check_printer():
    printer_config = open('printer.json')
    config = json.loads(printer_config.read())
    ip = config['ip']
    port = config['port']
    try:
        res = requests.get("http://" + ip + ":" + str(port) + '/?selftest')
        if res.json() and res.json()['success']:
            return {'success': True}
        else:
            return {'success': False}
    except Exception as e:
        print(e)
        return {'success': False, 'message':'Printer Connection Failed with self test request'}


@app.route("/find_printer", methods=["GET"])
def find_printer():
    # Scan Network for printer
    return "True"


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
