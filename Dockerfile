FROM spider:latest
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
