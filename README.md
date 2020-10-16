bilibili spider
=
    graduation project repo

#### Require

| |dependencies
---|------
db|sqlalchemy, postgreSQL
http|urllib3
s3|boto3, minio
xml|bs4, lxml
util|selfusepy
cache|redis

##### tips

    不再记录danmaku的信息
    tables(av_info, av_stat, user)
    multi_danmaku_v3_java 已弃用
    ids_spliced = [ids[i:i + size] for i in range(0, len(ids), size)]
    list.sort(key = lambda k: k["id"])
    注意引用传递
    use map.pop(key, None)
    multiprocess Pool要用Manage().Queue()