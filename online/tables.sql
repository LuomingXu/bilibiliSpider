drop table if exists av_info;
create table av_info
(
    aid                   bigint not null primary key,
    videos                int,
    tid                   int,
    tname                 varchar(255),
    copyright             int,
    pic                   varchar(255),
    title                 varchar(500),
    pubdate               datetime,
    ctime                 datetime,
    `desc`                varchar(2000),
    state                 int,
    attribute             int,
    duration              int,
    mission_id            bigint,
    dynamic               varchar(2000),
    cid                   bigint,
    bvid                  varchar(255),
    owner_mid             bigint comment '关联用户表',
    stat_aid              bigint comment '关联stat表',
    right_bp              tinyint,
    right_elec            tinyint,
    right_download        tinyint,
    right_movie           tinyint,
    right_pay             tinyint,
    right_hd5             tinyint,
    right_no_reprint      tinyint,
    right_autoplay        tinyint,
    right_ugc_pay         tinyint,
    right_is_cooperation  tinyint,
    right_ugc_pay_preview tinyint,
    right_no_background   tinyint,
    dimension_width       int,
    dimension_height      int,
    dimension_rotate      tinyint,
    last_update_time      datetime,
    create_time           datetime default current_timestamp
);
drop table if exists av_stat;
create table av_stat
(
    id           bigint   not null primary key auto_increment,
    aid          bigint   not null,
    create_time  datetime not null comment '记录这条数据的时间',
    view         int,
    danmaku      int,
    reply        int,
    favorite     int,
    coin         int,
    share        int,
    `rank`       tinyint comment '自己根据当前的顺序计算出来的顺序',
    now_rank     tinyint,
    his_rank     tinyint,
    `like`       int,
    dislike      int,
    online_count int comment '当前观看人数'
);
create index avStat_aid on av_stat (aid);
drop table if exists av_cids;
create table av_cids
(
    cid       bigint not null primary key,
    page      int    null,
    page_name varchar(500),
    aid       bigint not null
);
create index avCids_cid on av_cids (cid);
create index avCids_aid on av_cids (aid);

