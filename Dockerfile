FROM python:sprider
ADD /python /home/python
ENTRYPOINT python /home/python/main.py
