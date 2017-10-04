import unittest
from transform import image_transform, param_validation, InvalidParamsError
import PIL.Image
import os
from copy import copy

BASE_DIR = 'tests/data'


class ImageTranformTests(unittest.TestCase):

    def test_resize(self):
        filename = os.path.join(BASE_DIR, 'terminal.gif')  # 35x28
        operations = {'w': 50, 'h': 100}
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], operations['h']), img.size)

    def test_resize_with_fit(self):
        filename = os.path.join(BASE_DIR, 'terminal.gif')  # 35x28
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
        operations = {'w': w, 'h': h, 'auto': 'compress'}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, in_file_size)
        operations = {'auto': 'compress'}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, in_file_size)

    def test_format(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        in_file_size = os.stat(filename).st_size
        operations = {'fm': 'png'}
        output = image_transform(filename, operations)
        self.assertIn('png', output)
        self.assertGreater(os.stat(output).st_size, in_file_size)

        filename = os.path.join(BASE_DIR, 'terminal.gif')
        in_file_size = os.stat(filename).st_size
        operations = {'fm': 'jpeg', 'q': 10}
        output = image_transform(filename, operations)
        self.assertIn('jpeg', output)
        self.assertGreater(os.stat(output).st_size, in_file_size)

    def test_quality(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        in_file_size = os.stat(filename).st_size
        operations = {'q': 50}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, in_file_size)



class ParamValidationTests(unittest.TestCase):

    def test_valid(self):
        ops = {'width': 10, 'height': 20, 'fit': 'crop',
               'format': 'jpeg', 'quality': 75, 'auto': 'compress'}
        self.assertIsNotNone(param_validation(ops))
        ops = {'w': 10, 'h': 20, 'fit': 'crop',
                      'fm': 'jpeg', 'q': 75, 'auto': 'compress'}
        self.assertIsNotNone(param_validation(ops))
        ops = {'WIDTH': 10, 'height': 20, 'fit': 'CROP',
                      'fm': 'jpeg', 'q': 75, 'auto': 'compress'}
        self.assertIsNotNone(param_validation(ops))

    def test_dependencies(self):
        self.assertIsNotNone(param_validation({'w': 1}))
        self.assertIsNotNone(param_validation({'h': 1}))
        self.assertIsNotNone(param_validation({'fm': 'png'}))
        self.assertIsNotNone(param_validation({'q': 1}))
        self.assertIsNotNone(param_validation({'auto': 'compress'}))
        self.assertIsNotNone(param_validation({'dpr': 1}))

        #
        # `fit` is dependend of either `w` or `h`
        #
        with self.assertRaises(InvalidParamsError) as exc:
            param_validation({'fit': 'crop'})
        
        self.assertIn('fit', str(exc.exception))


    def test_invalid_schema(self):
        ops = {'width': 'invalid', 'height': 20, 'fit': 'crop',
                      'format': 'jpeg', 'quality': 75, 'auto': 'compress'}
        with self.assertRaises(InvalidParamsError) as exc:
            param_validation(ops)

        self.assertIn('schema', str(exc.exception))

        ops = {'width': 'invalid', 'height': 20, 'fit': 'invalid',
                      'format': 'jpeg', 'quality': 75, 'auto': 'compress'}
        with self.assertRaises(InvalidParamsError):
            param_validation(ops)

    def test_invalid_quality_fmt(self):
        ops = {'fm': 'gif', 'quality': 75}
        with self.assertRaises(InvalidParamsError) as exc:
            param_validation(ops)
        
        self.assertIn('lossy', str(exc.exception))
