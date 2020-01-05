drop table if exists cid_danmaku;
create table cid_danmaku
(
    cid        bigint not null,
    danmaku_id bigint not null
) comment 'av与弹幕关联表';
create index cidDanmaku_cid on cid_danmaku (cid);
create index cidDanmaku_danmakuId on cid_danmaku (danmaku_id);
drop table if exists danmaku;
create table danmaku
(
    id            bigint not null primary key comment 'B站数据库id',
    mode          tinyint comment '模式',
    font_size     tinyint comment '字体大小',
    font_color    int comment '颜色',
    send_time     datetime comment '发送时间戳',
    danmaku_pool  tinyint comment '弹幕池',
    danmaku_epoch decimal(32, 5) comment '弹幕出现时间',
    user_hash     bigint comment '用户Hash',
    user_id       bigint comment '用户id',
    content       varchar(1000) comment '弹幕内容'
) comment 'format: <d p="15.91600,1,25,16777215,1566961307,0,845a9310,20876693555642372">Content</d>.
弹幕出现时间,模式,字体大小,颜色,发送时间戳,弹幕池,用户Hash,数据库ID';
create index danmaku_userId on danmaku (user_id);
create index danmaku_userHash on danmaku (user_hash);
