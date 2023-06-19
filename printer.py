import base64
from io import BytesIO
from escpos.printer import Network
from PIL import  Image
def print_base64(image_path):
    try:# Connect to the printer
        printer = Network("192.168.1.100", port=9100)  # Replace with your printer's IP address and port
        printer.set(align='center', width=2, height=2)
        printer.image(image_path)
        # Cut the paper
        printer.cut()
        return True
    except Exception as e:
        print(e)
        return False

