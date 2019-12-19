from typing import MutableMapping

from minio import Minio

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
