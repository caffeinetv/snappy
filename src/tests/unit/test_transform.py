import unittest
import os
from copy import copy
import PIL.Image
from transform import image_transform, param_validation, InvalidParamsError
from snappy.settings import DEFAULT_QUALITY_RATE, AGRESSIVE_QUALITY_RATE, SUPPORTED_FORMATS


BASE_DIR = 'tests/data'


class ImageTranformTests(unittest.TestCase):

    def test_resize(self):
        filename = os.path.join(BASE_DIR, 'terminal.gif')  # 35x28
        operations = {'w': 50, 'h': 100}
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual((operations['w'], operations['h']), img.size)

        operations = {'w': 25}
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual(operations['w'], img.size[0])

        operations = {'h': 25}
        output = image_transform(filename, operations)
        img = PIL.Image.open(output)
        self.assertEqual(operations['h'], img.size[1])


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

    def test_auto_compress(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        w, h = PIL.Image.open(filename).size
        in_file_size = os.stat(filename).st_size

        w, h = PIL.Image.open(filename).size
        operations = {'q': AGRESSIVE_QUALITY_RATE}
        output = image_transform(filename, operations)
        size_with_metadata = os.stat(output).st_size
        self.assertLess(os.stat(output).st_size, in_file_size)

        # applies agressive quality and remove metadata
        operations = {'auto': 'compress'}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, in_file_size)
        size_with_no_metadata = os.stat(output).st_size
        self.assertLess(size_with_no_metadata, size_with_metadata)


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
        
        for fm in SUPPORTED_FORMATS:
            #FIXME: https://github.com/caffeinetv/snappy/issues/10
            if fm != 'webp':
                operations = {'fm': fm}
                output = image_transform(filename, operations)
                self.assertIn(fm, output)


    def test_quality(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        w, h = PIL.Image.open(filename).size
        #
        # applying no transformation with the default quality
        #
        operations = {'w': w, 'h': h}
        output = image_transform(filename, operations)
        out_file_size = os.stat(output).st_size
        
        operations = {'q': DEFAULT_QUALITY_RATE - 5}
        output = image_transform(filename, operations)
        self.assertLess(os.stat(output).st_size, out_file_size)


    def test_dpr(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        w, h = PIL.Image.open(filename).size
        dpr = 2
        operations = {'dpr': dpr}
        output = image_transform(filename, operations)
        ow, oh = PIL.Image.open(output).size
        self.assertEqual((w*dpr, h*dpr), (ow, oh))
        
        scale = 2
        w, h = w*scale, h*scale
        operations = {'dpr': dpr, 'w': w, 'h': h}
        output = image_transform(filename, operations)
        ow, oh = PIL.Image.open(output).size
        self.assertEqual((w*dpr, h*dpr), (ow, oh))


    def test_all_ops(self):
        filename = os.path.join(BASE_DIR, 'lincoln.jpg')
        side = 100
        dpr = 2
        operations = {'w': side,'h': side, 'fit': 'crop', 'fm': 'gif', 'dpr': dpr, 'q': 50, 'auto': 'compress'}
        output = image_transform(filename, operations)
        ow, oh = PIL.Image.open(output).size
        self.assertEqual((side*dpr, side*dpr), (ow, oh))





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
