import unittest
from transform import image_transform, param_validation, InvalidParamsError, make_response
import PIL.Image
import os
from copy import copy
from tests.unit.snappy.s3_tests import S3MockerBase

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
        ops = {'WIDTH': 10, 'height': 20, 'fit': 'bounds',
               'format': 'jpeg', 'quality': 75, 'auto': 'compress'}
        params = param_validation(ops)
        self.assertIn('w', params)
        ops = {'w': 10, 'h': 20, 'fit': 'CROP',
                      'fm': 'jpeg', 'q': 75, 'auto': 'compress'}
        params = param_validation(ops)
        self.assertIn('fit', params)
        ops = {'w': 10, 'h': 20, 'f': 'clip', 'dpr': 2,
                      'fm': 'jpeg', 'q': 75, 'auto': 'compress'}
        params = param_validation(ops)
        self.assertEqual(ops, params)

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
        params = param_validation({'fit': 'crop'})
        self.assertEqual(params, {})
        

    def test_invalid_schema(self):
        ops = {'width': 'invalid', 'h': 20, 'fit': 'crop',
                      'format': 'jpeg', 'quality': 75, 'auto': 'compress'}

        params =   param_validation(ops)
        self.assertNotIn('w', params)
        self.assertIn('h', params)
        self.assertIn('q', params)

        ops = {'h': 'invalid', 'w': 20, 'fit': 'invalid', 'dpr': 'invalid',
                      'format': 'jpeg', 'quality': 75, 'auto': 'compress'}
        params = param_validation(ops)
        self.assertNotIn('h', params)
        self.assertNotIn('dpr', params)
        self.assertNotIn('fit', params)
        self.assertIn('w', params)
        self.assertIn('fm', params)
        self.assertIn('auto', params)

    def test_invalid_quality_fmt(self):
        ops = {'fm': 'gif', 'q': 75}
        params = param_validation(ops)
        self.assertNotIn('q', params)
        self.assertIn('fm', params)

class HTTPTests(S3MockerBase):
    def test_make_response(self):
        test_cc = 'max-age=3600'
        bucket, key, body = self.put_s3(**{'CacheControl': test_cc})
        

