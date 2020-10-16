drop table if exists av_info;
create table av_info
(
    aid                   bigint not null
        constraint av_info_pkey
            primary key,
    videos                integer,
    tid                   integer,
    tname                 varchar(255),
    copyright             integer,
    pic                   varchar(255),
    title                 varchar(500),
    pubdate               timestamp,
    ctime                 timestamp,
    "desc"                varchar(2000),
    state                 integer,
    attribute             integer,
    duration              integer,
    mission_id            bigint,
    dynamic               varchar(2000),
    cid                   bigint,
    bvid                  varchar(255),
    owner_mid             bigint,
    stat_aid              bigint,
    right_bp              numeric,
    right_elec            numeric,
    right_download        numeric,
    right_movie           numeric,
    right_pay             numeric,
    right_hd5             numeric,
    right_no_reprint      numeric,
    right_autoplay        numeric,
    right_ugc_pay         numeric,
    right_is_cooperation  numeric,
    right_ugc_pay_preview numeric,
    right_no_background   numeric,
    dimension_width       integer,
    dimension_height      integer,
    dimension_rotate      numeric,
    last_update_time      timestamp,
    create_time           timestamp default CURRENT_TIMESTAMP
);

comment on column av_info.owner_mid is '关联用户表';

comment on column av_info.stat_aid is '关联stat表';

alter table av_info
    owner to postgres;

drop table if exists av_stat;
create table av_stat
(
    id           serial    not null
        constraint av_stat_pkey
            primary key,
    aid          bigint    not null,
    create_time  timestamp not null,
    view         integer,
    danmaku      integer,
    reply        integer,
    favorite     integer,
    coin         integer,
    share        integer,
    rank         numeric,
    now_rank     numeric,
    his_rank     smallint,
    "like"       integer,
    dislike      integer,
    online_count integer
);

comment on column av_stat.create_time is '记录这条数据的时间';

comment on column av_stat.online_count is '当前观看人数';

alter table av_stat
    owner to postgres;

create index avstat_aid
    on av_stat (aid);

-- drop table if exists av_cids;
-- create table av_cids
-- (
--     cid       bigint not null primary key,
--     page      int    null,
--     page_name varchar(500),
--     aid       bigint not null
-- );
-- create index avCids_cid on av_cids (cid);
-- create index avCids_aid on av_cids (aid);
