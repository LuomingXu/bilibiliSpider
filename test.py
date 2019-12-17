import os, time, random, multiprocessing
from multiprocessing import Pool
from db import log, engine
from sqlalchemy.engine import ResultProxy


def consumer():
  r = ''
  t = ''
  while True:
    n = yield r
    m = yield t
    if not n:
      return
    log.info('[CONSUMER] Consuming %s...' % n)
    log.info('[CONSUMER] Consuming %s...' % m)
    r = '200 OK'


def produce(c):
  c.send(None)
  n = 0
  while n < 5:
    n = n + 1
    log.info('[PRODUCER] Producing %s...' % n)
    c.send(n)
    r = c.send(n + 1)
    log.info('[PRODUCER] Consumer return: %s' % r)
    log.info('sleep')
    time.sleep(5)
  c.close()


import threading
import asyncio
from asyncio import Task

count = 0


async def hello(start_time: int):
  global count
  log.info('i: %s, start' % count)

  deleta = start_time + count * 2 - int(time.time())
  time.sleep(deleta if deleta > 0 else 0)
  count += 1

  log.info('io start')
  await io()
  log.info('io done')


async def io():
  log.info('io')
  time.sleep(0.1)


def func(cid: int):
  print(multiprocessing.current_process().name + str(cid))


if __name__ == '__main__':
  log.info('123')
# t = time.time()
# print(int(round(time.time()*1000)))
# time.sleep(0.1)
# print(int(round(time.time()*1000)))

# loop = asyncio.get_event_loop()
# start_time: int = int(time.time())
# tasks = [hello(start_time), hello(start_time), hello(start_time), hello(start_time), hello(start_time)]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

# c = consumer()
# produce(c)
