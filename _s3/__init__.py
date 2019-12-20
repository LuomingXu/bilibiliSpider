import json
import os
from typing import Set

import boto3
import selfusepy

from config import s3_bucket, s3_endpoint, s3_secret_key, s3_access_key, log
from _s3.Entity import Objects, DeleteObjects

session = boto3.session.Session(aws_access_key_id = s3_access_key, aws_secret_access_key = s3_secret_key)
client = session.client('s3', endpoint_url = s3_endpoint)


def get_all_objects_key() -> Set[str]:
  res: dict = client.list_objects_v2(Bucket = s3_bucket, Prefix = '')
  res.pop('ResponseMetadata')  # remove useless key's data
  obj: Objects = selfusepy.parse_json(json.dumps(res, default = str), Objects())
  object_keys: Set[str] = set()
  for item in obj.Contents:
    object_keys.add(item.Key)
  log.info('[s3] received %s objects' % object_keys.__len__())
  return object_keys


def download_objects(dir_to_save_files: str, keys: Set[str]) -> Set[str]:
  dirs: Set[str] = set()
  for key in keys:
    dirs.add(os.path.split(key)[0])

  for _dir in dirs:
    os.makedirs(dir_to_save_files + _dir, exist_ok = True)

  for key in keys:
    client.download_file(s3_bucket, key, dir_to_save_files + key)
    log.info('[s3 SAVED] %s' % key)

  return dirs


def delete_objects(keys: Set[str]):
  j: str = '{"Objects": [%s], "Quiet": true}' % ','.join('{"Key": "%s"}' % item for item in keys)
  client.delete_objects(Bucket = s3_bucket,
                        Delete = json.loads(j))
