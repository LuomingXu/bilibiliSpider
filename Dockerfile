FROM luomingxu/spider:base
RUN pip install selfusepy -U
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
