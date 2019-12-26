FROM luomingxu/spider:base
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
