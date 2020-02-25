package bilibilispider.multiprocess.online;

import lombok.Data;

import java.util.Date;
import java.util.List;

@Data
public class OnlineData {
    private Long aid;

    private Integer videos;

    private Integer tid;

    private String tname;

    private Integer copyright;

    private String pic;

    private String title;

    private Date pubdate;

    private Date ctime;

    private String desc;

    private Integer state;

    private Integer attribute;

    private Integer duration;

    private Long mission_id;

    private String redirect_url;

    private Rights rights;

    private Owner owner;

    private Stat stat;

    private String dynamic;

    private Long cid;

    private Dimension dimension;

    private Integer season_id;

    private String bvid;

    private Integer online_count;

    @Data
    public static class Rights {
        private Byte bp;

        private Byte elec;

        private Byte download;

        private Byte movie;

        private Byte pay;

        private Byte hd5;

        private Byte no_reprint;

        private Byte autoplay;

        private Byte is_cooperation;

        private Byte ugc_pay;

        private Byte ugc_pay_preview;

        private Byte no_background;
    }

    @Data
    public static class Owner {
        private Long mid;

        private String name;

        private String face;
    }

    @Data
    public static class Stat {
        private Long aid;

        private Integer view;

        private Integer danmaku;

        private Integer reply;

        private Integer favorite;

        private Integer coin;

        private Integer share;

        private Byte now_rank;

        private Short his_rank;

        private Integer like;

        private Integer dislike;
    }

    @Data
    public static class Dimension {
        private Integer width;

        private Integer height;

        private Byte rotate;
    }
}
