FROM luomingxu/spider:base
RUN pip install selfusepy --upgrade
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
