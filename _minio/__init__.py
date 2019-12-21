import os
from typing import MutableMapping, Set

from minio import Minio, ResponseError

from config import minio_endpoint, minio_access_key, minio_secret_key, minio_bucket, log

minioClient = Minio(minio_endpoint, access_key = minio_access_key, secret_key = minio_secret_key, secure = True)


def remove():
  obj = minioClient.list_objects(minio_bucket, prefix = 'online/')
  for item in obj:
    minioClient.remove_object(minio_bucket, item.object_name)
  obj = minioClient.list_objects(minio_bucket, prefix = 'danmaku/')
  for item in obj:
    minioClient.remove_object(minio_bucket, item.object_name)


def put(files: MutableMapping[str, str]):
  for item in files.items():
    file_name = item[0]
    file_path = item[1]

    try:
      minioClient.fput_object(bucket_name = minio_bucket, object_name = file_name,
                              file_path = file_path)
    except Exception as e:
      log.exception(e)
    else:
      log.info('[SAVED] %s' % file_path)


def get(_prefix: str = '', files: MutableMapping[str, Set[str]] = None) -> MutableMapping[str, Set[str]]:
  if files is None:
    files = {}

  objects = minioClient.list_objects(minio_bucket, prefix = _prefix)
  _dir = None
  for item in objects:
    object_name = item.object_name
    if str(object_name).endswith('/'):
      get(object_name)
    else:
      if _dir:
        files[_dir].add(object_name)
      else:
        _dir = str(os.path.split(object_name)[0])
        files[_dir] = set()
        files[_dir].add(object_name)

  return files


def download(files: MutableMapping[str, Set[str]]):
  for _dir in files.keys():
    os.makedirs('data-temp/' + _dir, exist_ok = True)

  for _set in files.values():
    for file_name in _set:
      try:
        data = minioClient.get_object(minio_bucket, file_name)

        f = open('data-temp/' + file_name, 'wb')
        for d in data.stream(32 * 1024):
          f.write(d)
      except ResponseError as e:
        log.exception(e)
      else:
        log.info(file_name)
