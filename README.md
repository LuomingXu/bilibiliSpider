bilibili spider
=
    graduation project repo

#### Require

purpose|dependency
---|------
db|sqlalchemy, pymysql
http|urllib3
s3|boto3, minio(archive)
xml|bs4, lxml
util|selfusepy
cache|redis

    ids_spliced = [ids[i:i + size] for i in range(0, len(ids), size)]
    注意引用传递
    _map(key, None)
    Pool要用Manage().Queue()