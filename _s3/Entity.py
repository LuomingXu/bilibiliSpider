from typing import List, Set

from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class Objects(BaseJsonObject):
  """
  s3 api list_objects_v2() result class
  """

  def __init__(self):
    self.IsTruncated: bool = False
    self.Contents: List[Objects.Contents] = [Objects.Contents()]
    self.Name: str = ''
    self.Prefix: str = ''
    self.Delimiter: str = ''
    self.MaxKeys: int = -1
    self.CommonPrefixes: List[Objects.CommonPrefixes] = [Objects.CommonPrefixes()]
    self.EncodingType: str = ''
    self.KeyCount: int = -1
    self.ContinuationToken: str = ''
    self.NextContinuationToken: str = ''
    self.StartAfter: str = ''

  @override_str
  class Contents(BaseJsonObject):

    def __init__(self):
      self.Key: str = ''
      self.LastModified: str = ''
      self.ETag: str = ''
      self.Size: int = -1
      self.StorageClass: str = ''
      self.Owner: Objects.Contents.Owner = Objects.Contents.Owner()

    @override_str
    class Owner(BaseJsonObject):

      def __init__(self):
        self.DisplayName: str = ''
        self.ID: str = ''

  @override_str
  class CommonPrefixes(BaseJsonObject):
    def __init__(self):
      self.Prefix: str = ''


class DeleteObjects(object):

  def __init__(self, keys: Set[str] = None):
    self.Objects: List[DeleteObjects.Objects] = self.__create_objects__(keys) if keys is not None else [
      DeleteObjects.Objects()]
    self.Quiet: bool = True

  def __create_objects__(self, keys: Set[str] = None) -> list:
    l: List[DeleteObjects.Objects] = []
    for key in keys:
      l.append(DeleteObjects.Objects(key))
    return l

  class Objects(BaseJsonObject):

    def __init__(self, key: str = None):
      self.Key: str = key if key is not None else ''
      self.VersionId: str = ''

  def __str__(self):
    return '{"Objects": [%s], "Quiet": true}' % ','.join('{"Key": "%s"}' % item.Key for item in self.Objects)
