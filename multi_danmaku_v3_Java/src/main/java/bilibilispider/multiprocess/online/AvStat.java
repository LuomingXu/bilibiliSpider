package bilibilispider.multiprocess.online;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import java.io.Serializable;
import java.util.Date;

@Data
@TableName("av_stat")
public class AvStat {
    public AvStat() {}

    public AvStat(OnlineData data, Byte rank, DateTime createTime) {
        this.aid = data.getStat().getAid();
        this.createTime = createTime.toDateTime(DateTimeZone.forOffsetHours(8)).toDate();
        this.view = data.getStat().getView();
        this.danmaku = data.getStat().getDanmaku();
        this.reply = data.getStat().getReply();
        this.favorite = data.getStat().getFavorite();
        this.coin = data.getStat().getCoin();
        this.share = data.getStat().getShare();
        this.rank = rank;
        this.nowRank = data.getStat().getNow_rank();
        this.hisRank = data.getStat().getHis_rank();
        this.like = data.getStat().getLike();
        this.dislike = data.getStat().getDislike();
        this.onlineCount = data.getOnline_count();
    }

    @TableId private Long id;

    private Long aid;

    /** 记录这条数据的时间 */
    private Date createTime;

    private Integer view;

    private Integer danmaku;

    private Integer reply;

    private Integer favorite;

    private Integer coin;

    private Integer share;

    @TableField("`rank`")
    private Byte rank;

    private Byte nowRank;

    private Short hisRank;

    @TableField("`like`")
    private Integer like;

    private Integer dislike;

    /** 当前观看人数 */
    private Integer onlineCount;
}
