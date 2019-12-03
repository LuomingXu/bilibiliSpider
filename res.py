#!/usr/bin/python
# encoding:UTF-8
import urllib3
import json
from urllib.parse import urlencode


class Request(object):
  def __init__(self):
    self.http = urllib3.PoolManager()
    self.UTF8 = 'utf-8'
    self.res: urllib3.response.HTTPResponse = None

  def get(self, url: str, **params: dict):
    """
    http get method
    :param url: URL
    :param params: http request params. should be class's dict. e.g., res.Request.get('https://example.com', **object.__dict__)
    :return:
    """
    if params is not None:
      self.res = self.http.request('GET', url, fields = params)
    else:
      self.res = self.http.request('GET', url)

  def put(self, url: str, body: object = None, **params: dict):
    """
    http put method
    :param url: URL
    :param body: put body. one object
    :return:
    """
    if params is not None:
      url += '?' + urlencode(params)
    if body is not None:
      self.res = self.http.request('PUT', url, body = json.dumps(body.__dict__),
                                   headers = {'Content-Type': 'application/json'})
    else:
      self.res = self.http.request('PUT', url)

  def post(self, url: str, body: object):
    """
    http post method
    :param url: URL
    :param body: post body. one object
    :return:
    """
    self.res = self.http.request('POST', url, body = json.dumps(body.__dict__),
                                 headers = {'Content-Type': 'application/json'})
