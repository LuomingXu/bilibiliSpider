from datetime import datetime
from typing import List, Set

from botocore.response import StreamingBody
from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class ResponseMetadata(BaseJsonObject):

  def __init__(self):
    self.RequestId: str = ''
    self.HostId: str = ''
    self.HTTPStatusCode: int = -1
    self.HTTPHeaders: dict = {}
    self.RetryAttempts: int = -1


@override_str
class Object(BaseJsonObject):
  """
  s3 api get_object() result class
  """

  def __init__(self):
    self.ResponseMetadata: ResponseMetadata = ResponseMetadata()
    self.Body: StreamingBody
    self.DeleteMarker: bool = False
    self.AcceptRanges: str = ''
    self.Expiration: str = ''
    self.Restore: str = ''
    self.LastModified: datetime
    self.ContentLength: int = -1
    self.ETag: str = ''
    self.MissingMeta: int = -1
    self.VersionId: str = ''
    self.CacheControl: str = ''
    self.ContentDisposition: str = ''
    self.ContentEncoding: str = ''
    self.ContentLanguage: str = ''
    self.ContentRange: str = ''
    self.ContentType: str = ''
    self.Expires: datetime
    self.WebsiteRedirectLocation: str = ''
    self.ServerSideEncryption: str = ''
    """
    AES256 | aws:kms
    """
    self.Metadata: dict = {}
    self.SSECustomerAlgorithm: str = ''
    self.SSECustomerKeyMD5: str = ''
    self.SSEKMSKeyId: str = ''
    self.StorageClass: str = ''
    """
    STANDARD | REDUCED_REDUNDANCY | STANDARD_IA | ONEZONE_IA | INTELLIGENT_TIERING | GLACIER | DEEP_ARCHIVE 
    """
    self.RequestCharged: str = ''
    self.ReplicationStatus: str = ''
    """
    COMPLETE | PENDING | FAILED | REPLICA
    """
    self.PartsCount: int = -1
    self.TagCount: int = -1
    self.ObjectLockMode: str = ''
    """
    GOVERNANCE | COMPLIANCE
    """
    self.ObjectLockRetainUntilDate: datetime
    self.ObjectLockLegalHoldStatus: str = ''


@override_str
class Objects_v2(BaseJsonObject):
  """
  s3 api list_objects_v2() result class
  """

  def __init__(self):
    self.IsTruncated: bool = False
    self.Contents: List[Objects_v2.Contents] = [Objects_v2.Contents()]
    self.Name: str = ''
    self.Prefix: str = ''
    self.Delimiter: str = ''
    self.MaxKeys: int = -1
    self.CommonPrefixes: List[Objects_v2.CommonPrefixes] = [Objects_v2.CommonPrefixes()]
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
      self.Owner: Objects_v2.Contents.Owner = Objects_v2.Contents.Owner()

    @override_str
    class Owner(BaseJsonObject):

      def __init__(self):
        self.DisplayName: str = ''
        self.ID: str = ''

  @override_str
  class CommonPrefixes(BaseJsonObject):
    def __init__(self):
      self.Prefix: str = ''


@override_str
class Objects(BaseJsonObject):
  """
  s3 api list_objects() result class
  """

  def __init__(self):
    self.IsTruncated: bool = False
    self.Marker: str = ''
    self.NextMarker: str = ''
    self.Contents: List[Objects.Contents] = [Objects.Contents()]
    self.Name: str = ''
    self.Prefix: str = ''
    self.Delimiter: str = ''
    self.MaxKeys: int = -1
    self.CommonPrefixes: List[Objects.CommonPrefixes] = [Objects.CommonPrefixes()]
    self.EncodingType: str = ''

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
