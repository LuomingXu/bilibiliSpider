create table "user"
(
    mid            bigint not null
        constraint user_pkey
            primary key,
    name           varchar(500),
    fans           integer,
    face           varchar(1000),
    rank           integer,
    level          integer,
    birthday       varchar(50),
    sign           varchar(500),
    fans_badge     smallint,
    vip_type       integer,
    vip_status     integer,
    official_title varchar(100),
    official_type  smallint,
    official_role  smallint
);

comment on table "user" is 'B站用户数据';

alter table "user"
    owner to postgres;
