import json
import os
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import Set, MutableMapping

import boto3
import selfusepy

from _s3.Entity import Objects_v2, Objects, DeleteObjects, Object
from config import minio_bucket, minio_access_key, minio_secret_key, minio_endpoint, log

s3_session = boto3.session.Session(aws_access_key_id = minio_access_key, aws_secret_access_key = minio_secret_key)
s3_client = s3_session.client('s3', endpoint_url = minio_endpoint)
s3_resource = s3_session.resource('s3', endpoint_url = minio_endpoint)
bucket = minio_bucket


def get_all_objects_key_v2() -> Set[str]:
  ContinuationToken = None
  object_keys: Set[str] = set()
  while True:
    args = dict(Bucket = bucket, Prefix = '')
    if ContinuationToken:
      args["ContinuationToken"] = ContinuationToken
    res: dict = s3_client.list_objects_v2(**args)
    res.pop('ResponseMetadata', None)  # remove useless key's data
    obj: Objects_v2 = selfusepy.parse_json(json.dumps(res, default = str), Objects_v2())
    if isinstance(obj.Contents, list):
      for item in obj.Contents:
        object_keys.add(item.Key)
    else:
      return object_keys

    if not obj.IsTruncated:
      break
    else:
      log.info('[s3] Got %s keys' % object_keys.__len__())
      ContinuationToken = obj.NextContinuationToken
  log.info('[s3] received %s objects' % object_keys.__len__())

  return object_keys


def get_all_objects_key() -> Set[str]:
  Marker = None
  object_keys: Set[str] = set()
  while True:
    args = dict(Bucket = bucket, Prefix = '')
    if Marker:
      args['Marker'] = Marker
    res: dict = s3_client.list_objects(**args)
    res.pop('ResponseMetadata', None)  # remove useless key's data
    obj: Objects = selfusepy.parse_json(json.dumps(res, default = str), Objects())
    if isinstance(obj.Contents, list):
      for item in obj.Contents:
        object_keys.add(item.Key)
    else:
      return object_keys

    if not obj.IsTruncated:
      break
    else:
      log.info('[s3] Got %s keys' % object_keys.__len__())
      Marker = obj.NextMarker

  log.info('[s3] received %s objects' % object_keys.__len__())
  return object_keys


def download_objects(dir_to_save_files: str, keys: Set[str]):
  dirs: Set[str] = set()
  for key in keys:
    dirs.add(os.path.split(key)[0])

  for _dir in dirs:
    os.makedirs(dir_to_save_files + _dir, exist_ok = True)

  for i, key in enumerate(keys):
    s3_client.download_file(bucket, key, dir_to_save_files + key)
    log.info('[s3 SAVED] i: %s, %s' % (i, key))


def delete_objects(keys: Set[str]):
  """
  client.delete_objects() The request contains a list of up to 1000 keys that you want to delete.
  changed to batch deletion ver
  """
  temp: Set[str] = set()
  for item in keys:
    temp.add(item)
    if temp.__len__() % 1000 == 0:
      j: str = '{"Objects": [%s], "Quiet": true}' % ','.join('{"Key": "%s"}' % item for item in temp)
      s3_client.delete_objects(Bucket = bucket,
                               Delete = json.loads(j))
      temp = set()
  j: str = '{"Objects": [%s], "Quiet": true}' % ','.join('{"Key": "%s"}' % item for item in temp)
  s3_client.delete_objects(Bucket = bucket,
                           Delete = json.loads(j))


def put(files: MutableMapping[str, str]):
  for file_name, file_path in files.items():
    try:
      s3_client.upload_file(Filename = file_path, Bucket = bucket, Key = file_name)
    except BaseException as e:
      raise e
    else:
      log.info('[PUT] %s' % file_name)


def update_object_metadata(key: str, metadata: dict):
  obj = s3_resource.Object(bucket, key)
  obj.metadata.update(metadata)
  obj.copy_from(CopySource = {'Bucket': bucket, 'Key': key}, Metadata = obj.metadata,
                MetadataDirective = 'REPLACE')


def get_object(key: str) -> Object:
  d: dict = s3_client.get_object(Bucket = bucket, Key = key)
  obj = selfusepy.parse_json(json.dumps(d, default = str), Object())
  obj.Body = d['Body']
  return obj


def archive_object(keys: Set[str]) -> bool:
  for key in keys:
    res: dict = s3_client.copy_object(Bucket = 'archive',
                                      CopySource = {'Bucket': bucket, 'Key': key},
                                      Key = key, StorageClass = 'REDUCED_REDUNDANCY')
    if 'ETag' in res['CopyObjectResult'].keys():
      s3_client.delete_object(Bucket = bucket, Key = key)
    else:
      return False
  return True


def upload(data, upload_id, key, i):
  log.info("upload file part: %s" % i)
  res = s3_client.upload_part(Bucket = bucket, Key = key, PartNumber = i,
                              UploadId = upload_id, Body = data)
  part: dict = {
    'ETag': res.get('ETag'),
    'PartNumber': i
  }
  return part


def part_upload(filepath: str, key: str) -> bool:
  res: dict = s3_client.create_multipart_upload(Bucket = bucket, Key = key)
  upload_id = res['UploadId']
  log.info(upload_id)
  pool = Pool(processes = 10)
  res: Set[ApplyResult] = set()
  parts: dict = {'Parts': list()}
  try:
    with open(filepath, 'r+b') as f:
      i: int = 1
      while True:
        data = f.read(50 * 1024 * 1024)  # 50mb each part
        if data == b'':
          break
        res.add(pool.apply_async(func = upload, args = (data, upload_id, key, i,)))
        i += 1

    pool.close()
    pool.join()

    for item in res:
      v = item.get()
      parts.get('Parts').append(v)

    s3_client.complete_multipart_upload(Bucket = bucket, Key = key, UploadId = upload_id, MultipartUpload = parts)

    return True
  except Exception as e:
    log.exception(e)
    log.warn("Abort %s" % abort_part_upload(key, upload_id))
    return False


def abort_part_upload(key: str, upload_id: str) -> bool:
  s3_client.abort_multipart_upload(Bucket = bucket, Key = key, UploadId = upload_id)

  return True
