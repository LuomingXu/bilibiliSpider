import binascii
from typing import List
from selfusepy.utils import Logger
from db import engine
from crc32.DO import crc32DO
from sqlalchemy.engine import ResultProxy

log = Logger().logger


def get_value(hash: str) -> (int, str):
  sql: str = 'select value from crc32 where hash = %s' % int(hash, 16)
  conn = engine.connect()
  try:
    res: ResultProxy = conn.execute(sql)
    return res.rowcount, ','.join('%s' % item[0] for item in res.fetchall())
  except Exception as e:
    log.error('sql: %s' % sql)
    log.exception(e)
  finally:
    conn.close()


if __name__ == '__main__':
  hashes: List[crc32DO] = []
  conn = engine.connect()
  for i in range(3_1908_0001, 5_0000_0000):
    hashes.append(crc32DO(binascii.crc32(str(i).encode("utf-8")), i))

    if i % 6_0000 == 0:
      log.info('i: %s' % i)

      sql: str = "insert into crc32(hash, value) values %s" % (', '.join('%s' % item.__str__() for item in hashes))
      hashes.clear()

      try:
        conn.execute(sql)
      except Exception as e:
        log.exception(e)
        exit(0)

      log.info('Done')
