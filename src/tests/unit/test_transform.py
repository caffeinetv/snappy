import unittest
from transform import image_transform
import PIL.Image
import os

BASE_DIR = 'tests/data'

class ImageTranformTests(unittest.TestCase):

	def test_resize(self):
		filename = os.path.join(BASE_DIR, 'terminal.gif') # 35x28
		operations = {'w': 50, 'h': 100}
		output = image_transform(filename, operations)
		img = PIL.Image.open(output)
		self.assertEqual((operations['w'], operations['h']), img.size)


