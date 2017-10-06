import unittest
from moto import mock_s3
from snappy.s3 import get_aws_resource, download_s3_obj, get_s3_obj
from snappy.utils import rnd_str

class S3MockerBase(unittest.TestCase):

    def get_main_bucket(self):
        return 'main_bucket'

    def setUp(self):
        self.s3_mock = mock_s3()
        self.s3_mock.start()
        self.s3_resource = get_aws_resource('s3')
        self.main_bucket = self.get_main_bucket()
        self.s3_resource.create_bucket(Bucket=self.main_bucket)
        super(S3MockerBase, self).setUp()

    def tearDown(self):
        self.s3_mock.stop()
        super(S3MockerBase, self).tearDown()

    def put_s3(self, bucket=None, key=None, body=None, **kwargs):
        if not bucket:
            bucket = self.main_bucket
        if not key:
            key = rnd_str(5)
        if not body:
            body = rnd_str(5)

        self.s3_resource.Bucket(bucket).put_object(Key=key, Body=body.encode(), **kwargs)
        return bucket, key, body
        
class S3Tests(S3MockerBase):
    def test_download_file(self):
        bucket, key, body = self.put_s3()
        filename = download_s3_obj(bucket, key)
        with open(filename) as fp:
            self.assertEqual(fp.read(), body)

    def test_file_not_found(self):
        bucket, key, body = self.put_s3()
        self.assertIsNone(download_s3_obj(bucket, key + 'wont_find'))
        self.assertIsNone(download_s3_obj(bucket + 'wont_find' , key))

    def test_get_obj(self):
        test_cc = 'max-age=3600'
        bucket, key, body = self.put_s3(**{'CacheControl': test_cc})
        obj = get_s3_obj(bucket, key)
        self.assertEqual(obj.cache_control, test_cc)

    def test_obj_not_found(self):
        bucket, key, body = self.put_s3()
        self.assertIsNone(get_s3_obj(bucket, key + 'wont_find'))
        self.assertIsNone(get_s3_obj(bucket + 'wont_find' , key))


        


