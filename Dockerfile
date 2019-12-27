FROM luomingxu/spider:base
RUN pip install selfusepy
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
