from datetime import date
from io import BytesIO, StringIO
from urllib.parse import urlparse

from fsspec.implementations.memory import MemoryFile


# TODO use the storage from the MemoryFileSystem instead, right now the information
# in both fakes will not be consistent
class FakeS3Client:
    def __init__(self, storage, **kwargs):
        self.storage = storage


    def get_storage(self):
        return self.storage

    def __map_entry_to_content(self, key):
        entry = self.storage[key]
        mod_date = entry.modified
        content = {
            'ETag': key,
            'Key': key,
            'LastModified': mod_date,
            'Size': len(entry.getvalue()),
            'StorageClass': 'STANDARD',
        }
        return content

    def list_objects_v2(self, **kwargs):
        bucket = kwargs["Bucket"]
        # bucket = 'lumigator-storage'
        prefix = kwargs["Prefix"]
        # prefix = 'datasets/d35c1eb7-db82-4a43-9881-180bed9d9808/dataset.csv'
        return {
            "IsTruncated": False,
            "Name": bucket,
            "KeyCount": len(self.storage),
            "Prefix": prefix,
            "Contents": [self.__map_entry_to_content(key) for key in self.storage.keys()]
        }

    def generate_presigned_url(self, method, **kwargs):
        # method = 'get_object'
        # expire_time = kwargs["ExpiresIn"]
        # expire_time = 3600
        params = kwargs["Params"]
        bucket = params["Bucket"]
        path = params["Key"]
        # params = {'Bucket': 'lumigator-storage', 'Key': 'datasets/d35c1eb7-db82-4a43-9881-180bed9d9808/dataset.csv/data-00000-of-00001.arrow'}
        return f'http://example.org/{bucket}/{path}'
