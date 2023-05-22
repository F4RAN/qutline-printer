import base64
from io import BytesIO
from PIL import Image
from escpos.printer import Network

def print_base64(base64_image):
    encoded_data = base64_image.split(",")[1]
    try:# Connect to the printer
        printer = Network("192.168.1.100", port=9100)  # Replace with your printer's IP address and port

        # # # Set the image printing parameters (adjust as needed)
        # printer.set(align='center', width=2, height=2)

        # Decode the base64 image
        # base64_image = "your_base64_image_here"  # Replace with your base64-encoded image
        image_data = base64.b64decode(encoded_data)

        # # Create a PIL image from the image data
        image = Image.open(BytesIO(image_data))

        # # # Convert the image to grayscale if needed
        image = image.convert("L")

        # # # Print the image
        printer.image(image)

        # Cut the paper
        printer.cut()
        return True
    except Exception as e:
        print(e)
        return False
