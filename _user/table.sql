create table bilibili
(
    mid            bigint        not null
        primary key,
    name           varchar(500)  null,
    face           varchar(1000) null,
    `rank`         int           null,
    level          int           null,
    birthday       varchar(50)   null,
    sign           varchar(500)  null,
    fans_badge     tinyint       null,
    vip_type       int           null,
    vip_status     int           null,
    official_title varchar(100)  null,
    official_type  tinyint       null,
    official_role  tinyint       null
)
    comment 'B站用户数据';