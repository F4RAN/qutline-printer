import base64
from io import BytesIO
from escpos.printer import Network
from generator.receipt import generate_receipt
from PIL import  Image,ImageGrab
def print_base64(image_path):
    print(image_path)
    # encoded_data = base64_image.split(",")[1]
    try:# Connect to the printer
        printer = Network("192.168.1.100", port=9100)  # Replace with your printer's IP address and port
        # Decode the base64 image

        # # Create a PIL image from the image data
        # image = Image.open("parsajan.jpg")

        # # Capture a screenshot of the screen
        # screenshot = ImageGrab.grab()

        # # Overlay the base64 image on the screenshot
        # screenshot.paste(image, (0, 0))

        # # Save the screenshot to a file
        # screenshot.save("screenshot.png")
        # # # Set the image printing parameters (adjust as needed)
        # printer.set(align='center', width=2, height=2)

        # Decode the base64 image
        # base64_image = "your_base64_image_here"  # Replace with your base64-encoded image
        # image_data = base64.b64decode(encoded_data)

        # # Create a PIL image from the image data
        # image = Image.open(BytesIO(image_data))
        # new_size = (image.size[0] // 2, image.size[1] // 2)  # Adjust the scaling factor as desired
        # resized_image = image.resize(new_size)
        # Convert the image to grayscale if needed
        # image = image.convert("L")
        # canvas = image.load()
        # buffer = BytesIO()
        # image.save("test.jpeg", format="JPEG")
        
        # base64_image = "your_base64_image_here"  # Replace with your base64-encoded image
        # image_data = base64.b64decode(encoded_data)

        # output_file = "output_image.jpg"  # Replace with your desired output file name

        # with open(output_file, "wb") as file:
        #     file.write(image_data)
        # # # Print the image
        # receipt = generate_receipt()
        # # Save the image to a BytesIO object
        # image_buffer = BytesIO()
        # receipt.save(image_buffer, format="PNG")
        # image_buffer.seek(0)
        printer.image(image_path)

        # Cut the paper
        # printer.cut()
        return True
    except Exception as e:
        print(e)
        return False

