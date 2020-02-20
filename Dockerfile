FROM luomingxu/spider:base
RUN pip install -U --force-reinstall selfusepy
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
