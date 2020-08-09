FROM python:3.7-slim-stretch
ADD ./ /home/python
WORKDIR /home/python
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple/
ENTRYPOINT python /home/python/main.py
