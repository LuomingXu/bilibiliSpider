import json
import os
from typing import Set, MutableMapping

import boto3
import selfusepy

from _s3.Entity import Objects_v2, Objects, DeleteObjects
from config import s3_tx_bucket, s3_tx_endpoint, s3_tx_access_key, s3_tx_secret_key, log

tx_session = boto3.session.Session(aws_access_key_id = s3_tx_access_key, aws_secret_access_key = s3_tx_secret_key)
tx_client = tx_session.client('s3', endpoint_url = s3_tx_endpoint)


def get_all_objects_key_v2() -> Set[str]:
  res: dict = tx_client.list_objects_v2(Bucket = s3_tx_bucket, Prefix = '')
  res.pop('ResponseMetadata', None)  # remove useless key's data
  obj: Objects_v2 = selfusepy.parse_json(json.dumps(res, default = str), Objects_v2())
  object_keys: Set[str] = set()
  for item in obj.Contents:
    object_keys.add(item.Key)
  log.info('[s3] received %s objects' % object_keys.__len__())
  return object_keys


def get_all_objects_key() -> Set[str]:
  Marker = None
  object_keys: Set[str] = set()
  while True:
    args = dict(Bucket = s3_tx_bucket, Prefix = '')
    if Marker:
      args['Marker'] = Marker
    res: dict = tx_client.list_objects(**args)
    res.pop('ResponseMetadata', None)  # remove useless key's data
    obj: Objects = selfusepy.parse_json(json.dumps(res, default = str), Objects())
    for item in obj.Contents:
      object_keys.add(item.Key)

    if not obj.IsTruncated:
      break
    else:
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
    tx_client.download_file(s3_tx_bucket, key, dir_to_save_files + key)
    log.info('[s3 SAVED] i: %s, %s' % (i, key))


def delete_objects(keys: Set[str]):
  j: str = '{"Objects": [%s], "Quiet": true}' % ','.join('{"Key": "%s"}' % item for item in keys)
  tx_client.delete_objects(Bucket = s3_tx_bucket,
                           Delete = json.loads(j))


def put(files: MutableMapping[str, str]):
  for file_name, file_path in files.items():
    try:
      tx_client.upload_file(Filename = file_path, Bucket = s3_tx_bucket, Key = file_name)
    except Exception as e:
      raise e
    else:
      log.info('[PUT] %s' % file_name)
