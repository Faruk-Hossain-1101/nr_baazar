import os
import barcode
from django.conf import settings
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
from django.contrib.staticfiles import finders

def create_label(SKU, barcode_value, size, price, selling_price, color=None, cell=None):
    # Define label dimensions (38x25mm in pixels, assuming 300 DPI for high quality)
    label_width = 38 * 11.811  # 38mm to pixels (1mm = 11.811 pixels at 300 DPI)
    label_height = 25 * 11.811  # 25mm to pixels (1mm = 11.811 pixels at 300 DPI)
    
    # Create a blank image with a white background
    label_image = Image.new('RGB', (int(label_width), int(label_height)), 'white')
    draw = ImageDraw.Draw(label_image)
    
    static_font_path = finders.find('roboto/Roboto-Black.ttf')
    # Set up font for header (larger font size)
    try:
        header_font = ImageFont.truetype(static_font_path, 50)  # Bold, large font for header
    except IOError:
        header_font = ImageFont.load_default()

    # Draw header "NR BAAZAR" centered at the top
    header_text = "NR BAAZAR"
    header_bbox = draw.textbbox((0, 0), header_text, font=header_font)  # Get bounding box for the header
    header_width = header_bbox[2] - header_bbox[0]  # Calculate width from bbox
    header_height = header_bbox[3] - header_bbox[1]  # Calculate height from bbox
    header_x_offset = (label_width - header_width) / 2  # Center the header
    draw.text((header_x_offset, 5), header_text, font=header_font, fill="black")
    
    # Set up font for larger text (for SKU, Size, Price)
    try:
        font = ImageFont.truetype(static_font_path, 35)  # Bold font for other text
    except IOError:
        font = ImageFont.load_default()
    try:
        price_font = ImageFont.truetype(static_font_path, 35)  # Bold font for other text
    except IOError:
        price_font = ImageFont.load_default()

    # Draw text (Size, Price, Color)
    y_offset = header_height + 15  # Start below the header
    draw.text((5, y_offset), f"SKU: {SKU}", font=font, fill="black")
    if size:
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Size: {size}", font=font, fill="black")
    else:
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Size: Free", font=font, fill="black")

    if cell:
        draw.text((200, y_offset), f"Cell: {cell}", font=font, fill="black")
    
    if color:
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Color: {color}", font=font, fill="black")

    if price > selling_price:
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Price: {price}", font=price_font, fill="black")
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Offer Price: {selling_price}", font=price_font, fill="black")
    else:
        y_offset += 45  # Increased offset for larger text
        draw.text((5, y_offset), f"Price: {price}", font=price_font, fill="black")

    
    # Generate barcode (24x8mm, convert to pixels for 300 DPI)
    barcode_generator = barcode.get_barcode_class('code128')  # Choose barcode type
    barcode_instance = barcode_generator(barcode_value, writer=ImageWriter())

    # Set barcode width and height for 24x8mm (converted to pixels)
    barcode_width = 20 * 11.811  # 24mm to pixels
    barcode_height = 8 * 11.811  # 10mm to pixels
    
    # Set barcode writer's options for width and height
    barcode_writer = barcode_instance.writer
    barcode_writer.set_options({'module_width': 0.2, 'module_height': 10})  # Adjust height and width
    
    # Render the barcode to an image
    barcode_image = barcode_instance.render()

    # Resize barcode to 24x10mm (converted to pixels) if necessary
    barcode_image = barcode_image.resize((int(barcode_width), int(barcode_height)))

    # Rotate the barcode counterclockwise 90 degrees
    barcode_image = barcode_image.rotate(90, expand=True)

    # Calculate the position for the barcode on the right side (keeping the barcode's 12mm width)
    barcode_x_offset = int(label_width - barcode_height)  # Place barcode on the right
    barcode_y_offset = int(label_height - barcode_image.height - 5)  # Center vertically

    # Paste the rotated barcode onto the label
    label_image.paste(barcode_image, (barcode_x_offset, barcode_y_offset))

    # Save the label image with SKU as filename
    media_folder = settings.MEDIA_ROOT
    if not os.path.exists(media_folder):
        os.makedirs(media_folder)

    # Save the label image with SKU as filename in the 'media' folder
    label_image_path = os.path.join(media_folder, f"{SKU}.png")
    label_image.save(label_image_path)

    return label_image_path