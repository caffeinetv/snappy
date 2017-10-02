import unittest
from transform import image_transform
import PIL.Image
import os
from copy import copy

BASE_DIR = 'tests/data'

class ImageTranformTests(unittest.TestCase):

    def test_resize(self):
        filename = os.path.join(BASE_DIR, 'terminal.gif') # 35x28
        operations = {'w': 50, 'h': 100}
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], operations['h']), img.size)

    def test_resize_with_fit(self):
        filename = os.path.join(BASE_DIR, 'terminal.gif') # 35x28
        base_ops = {'w': 50, 'h': 100}
        
        operations = copy(base_ops)
        operations.update({'fit': 'clip'})
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], operations['h']), img.size)

        operations = copy(base_ops)
        operations.update({'fit': 'crop'})
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], operations['h']), img.size)

        #
        # bounds will fit only one the dimensions
        # in case the aspect ratio is different
        #
        operations = copy(base_ops)
        operations.update({'fit': 'bounds'})
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], 40), img.size)

    def test_compress(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        w, h = PIL.Image.open(filename).size
        in_file_size = os.stat(filename).st_size
        print(in_file_size)
        operations = {'w': w, 'h': h, 'auto': 'compress'}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, in_file_size)
        print(os.stat(output).st_size)





