FROM luomingxu/spider:base
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
ADD ./ /home/python
ENTRYPOINT python /home/python/main.py
