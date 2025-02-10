import os
from django.test import TestCase
from django.conf import settings
from PIL import Image
from shop.utils.barcode import create_label  

class CreateLabelTestCase(TestCase):
    def setUp(self):
        self.SKU = "TEST1234"
        self.barcode_value = "123456789012"
        self.size = "L"
        self.price = 500
        self.selling_price = 450
        self.color = "Red"
        self.cell = "A1"
        self.media_folder = settings.MEDIA_ROOT

    def test_create_label_success(self):
        # Call the function
        label_path = create_label(self.SKU, self.barcode_value, self.size, self.price, self.selling_price, self.color, self.cell)
        
        # Check if the label was created
        self.assertTrue(os.path.exists(label_path), "Label image was not created.")
        
        # Check if the generated file is a valid image
        with Image.open(label_path) as img:
            self.assertEqual(img.format, "PNG", "Generated label is not a PNG image.")
        
        # Cleanup
        os.remove(label_path)
    
    def test_create_label_success_without_size(self):
        size= None
        # Call the function
        label_path = create_label(self.SKU, self.barcode_value, size, self.price, self.selling_price, self.color, self.cell)
        
        # Check if the label was created
        self.assertTrue(os.path.exists(label_path), "Label image was not created.")
        
        # Check if the generated file is a valid image
        with Image.open(label_path) as img:
            self.assertEqual(img.format, "PNG", "Generated label is not a PNG image.")
        
        # Cleanup
        os.remove(label_path)

    def tearDown(self):
        # Ensure cleanup after test
        label_path = os.path.join(self.media_folder, f"{self.SKU}.png")
        if os.path.exists(label_path):
            os.remove(label_path)
