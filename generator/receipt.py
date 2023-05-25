from PIL import Image, ImageDraw, ImageFont
import os

pointer = 0
def draw_item(draw,item, quantity, _, depth=0):
     # Kesafat kari shoroo
    width = 560
    height = 800
    receipt = Image.new("RGB", (width, height), "white")
    header_height = 120
    table_y = header_height + 150
    table_cell_width = 500
    table_cell_height = 30
    table_padding = 10
    header_color = "#333333"
    text_color = "#000000"
    script_directory = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_directory, "arial.ttf")
    bold_font_path = os.path.join(script_directory, "arial-bold.ttf")
    logo_path = os.path.join(script_directory, "logo.png")
    header_font = ImageFont.truetype(font_path, 24)
    store_name_font = ImageFont.truetype(font_path, 36)
    table_name_font = ImageFont.truetype(font_path, 18)
    order_number_font = ImageFont.truetype(bold_font_path, 48)
    item_font = ImageFont.truetype(font_path, 24)
    sub_item_font = ImageFont.truetype(font_path, 18)
    sub_sub_item_font = ImageFont.truetype(font_path, 14)
    quantity_font = ImageFont.truetype(font_path, 24)
    order_id_font = ImageFont.truetype(font_path, 24)
    
    # Kesafat kari tamam
    pointer_sub = 0
    global pointer
    item_x = 10
    item_y = pointer + table_y + depth * (table_cell_height + table_padding)
    draw.text((item_x, item_y), item, font=item_font, fill=text_color)

    quantity_x = 200 + width - table_cell_width / 2 - 10
    quantity_y = pointer + table_y + depth * (table_cell_height + table_padding)
    draw.text((quantity_x, quantity_y), quantity, font=quantity_font, fill=text_color)

    if len(item) > 2:
        sub_items = _
        for i, (sub_item, sub_quantity, _) in enumerate(sub_items):

            sub_item_x = item_x + 30
            sub_item_y = pointer_sub + item_y + (i + 1) * (table_cell_height + table_padding)

            draw.text((sub_item_x, sub_item_y), sub_item, font=sub_item_font, fill=text_color)
            pointer += 40
            sub_quantity_x = 100 + width - table_cell_width / 2 - 10
            sub_quantity_y = pointer_sub + item_y + (i + 1) * (table_cell_height + table_padding)
            draw.text((sub_quantity_x, sub_quantity_y), sub_quantity, font=quantity_font, fill=text_color)

            if len(sub_item) > 2:
                sub_sub_items = _
                for j, (sub_sub_item, sub_sub_quantity) in enumerate(sub_sub_items):
                    pointer_sub += 40
                    sub_sub_item_x =  sub_item_x + 30
                    sub_sub_item_y = (sub_item_y + (j + 1) * (table_cell_height + table_padding))
                    pointer += 40
                    draw.text((sub_sub_item_x, sub_sub_item_y), sub_sub_item, font=sub_sub_item_font, fill=text_color)

                    sub_sub_quantity_x = width - table_cell_width / 2 - 10
                    sub_sub_quantity_y = sub_item_y + (j + 1) * (table_cell_height + table_padding)
                    draw.text((sub_sub_quantity_x, sub_sub_quantity_y), sub_sub_quantity, font=quantity_font,
                              fill=text_color)

def generate_receipt():
        # Get the absolute path to the font file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_directory, "arial.ttf")
    bold_font_path = os.path.join(script_directory, "arial-bold.ttf")
    logo_path = os.path.join(script_directory, "logo.png")

    # Create a blank image with a white background
    width = 560
    height = 800
    receipt = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(receipt)

    # Define colors and fonts
    header_color = "#333333"
    text_color = "#000000"
    header_font = ImageFont.truetype(font_path, 24)
    store_name_font = ImageFont.truetype(font_path, 36)
    table_name_font = ImageFont.truetype(font_path, 18)
    order_number_font = ImageFont.truetype(bold_font_path, 48)
    item_font = ImageFont.truetype(font_path, 24)
    sub_item_font = ImageFont.truetype(font_path, 18)
    sub_sub_item_font = ImageFont.truetype(font_path, 14)
    quantity_font = ImageFont.truetype(font_path, 24)
    order_id_font = ImageFont.truetype(font_path, 24)

    # Draw header
    header_height = 120
    header_logo = Image.open(logo_path).resize((100, 100)).convert("RGBA")

    # Calculate the position to paste the logo with an offset
    logo_bg = Image.new("RGB", (100, 100), "white")
    logo_bg.paste(header_logo, (0, 0), mask=header_logo)

    receipt.paste(logo_bg, (10, 15))
    store_name = "Store Name"
    store_name_width, store_name_height = draw.textsize(store_name, font=store_name_font)
    store_name_x = (width - store_name_width) // 2
    draw.text((store_name_x, 15), store_name, font=store_name_font, fill=text_color)

    table_name = "Table Name"
    table_name_width, table_name_height = draw.textsize(table_name, font=table_name_font)
    table_name_x = (width - table_name_width) // 2
    draw.text((table_name_x, 135), table_name, font=table_name_font, fill=text_color)

    order_number = "5"
    order_number_font = ImageFont.truetype(bold_font_path, 72)
    order_number_width, order_number_height = draw.textsize(order_number, font=order_number_font)
    order_number_x = width - order_number_width - 10
    order_number_y = 15 + (header_height - order_number_height) // 2
    draw.rectangle(
        (order_number_x - 100, order_number_y - 5, order_number_x + order_number_width * 2 + 5,
        order_number_y + order_number_height * 2 + 5),
        fill="#cccccc"
    )
    draw.text((order_number_x - 50, order_number_y + 10), order_number, font=order_number_font, fill=text_color)

    # Draw table
    table_y = header_height + 150
    table_cell_width = 500
    table_cell_height = 30
    table_padding = 10

    items = [
        ("Food Name 1", "2x", [
            ("Sub-Food 1", "1x", [
                ("Sub-Sub-Food 1", "1x"),
                ("Sub-Sub-Food 2", "2x")
            ]),
            ("Sub-Food 2", "1x", [])
        ]),
        ("Food Name 2", "3x", [
            ("Sub-Food 3", "2x", []),
            ("Sub-Food 4", "1x", [
                ("Sub-Sub-Food 3", "1x"),
                ("Sub-Sub-Food 4", "2x"),
                ("Sub-Sub-Food 5", "3x")
            ])
        ]),
        ("Food Name 3", "1x", [])
    ]

    for i, (item, quantity, _) in enumerate(items):
        draw_item(draw,item, quantity, _, depth=i)

    # Draw order ID
    order_id = "Order ID: 123456789"
    order_id_width, order_id_height = draw.textsize(order_id, font=order_id_font)
    draw.text((10, height - order_id_height - 10), order_id, font=order_id_font, fill=text_color)
    
    # Save the receipt image
    
    return receipt
