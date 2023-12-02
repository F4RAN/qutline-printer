import base64
from io import BytesIO
from escpos.printer import Network
from PIL import  Image
import qrcode
from PIL import ImageOps

def print_base64(image_path):
    try:# Connect to the printer
        printer = Network("192.168.1.100", port=9100)  # Replace with your printer's IP address and port
        printer.set(align='center', width=2, height=3)
        printer.image(image_path)
        # Cut the paper
        printer.cut()
        return True
    except Exception as e:
        print(e)
        return False

def qr_generate():
    qr = qrcode.QRCode(
    version=3,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=9,
    border=9,
    )
    qr.add_data('https://dev.vitalize.dev/friends-kabob?table=617ae11a852c641245468282')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    padding= 3
    img_with_padding = ImageOps.expand(img, border=padding, fill="white")
    img_with_padding.save("qr_code.jpg")
    print_base64("../qr_code.jpg")

qr_generate()