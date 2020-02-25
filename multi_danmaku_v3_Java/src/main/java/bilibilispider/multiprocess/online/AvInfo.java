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
@TableName("av_info")
public class AvInfo {

    public AvInfo() {}

    public AvInfo(OnlineData data) {
        this.aid = data.getAid();
        this.videos = data.getVideos();
        this.tid = data.getTid();
        this.tname = data.getTname();
        this.copyright = data.getCopyright();
        this.pic = data.getPic();
        this.title = data.getTitle();
        this.pubdate =
                new DateTime(data.getPubdate()).toDateTime(DateTimeZone.forOffsetHours(8)).toDate();
        this.ctime =
                new DateTime(data.getCtime()).toDateTime(DateTimeZone.forOffsetHours(8)).toDate();
        this.desc = data.getDesc();
        this.state = data.getState();
        this.attribute = data.getAttribute();
        this.duration = data.getDuration();
        this.missionId = data.getMission_id();
        this.dynamic = data.getDynamic();
        this.cid = data.getCid();
        this.bvid = data.getBvid();
        this.ownerMid = data.getOwner().getMid();
        this.statAid = data.getStat().getAid();
        this.rightBp = data.getRights().getBp();
        this.rightElec = data.getRights().getElec();
        this.rightDownload = data.getRights().getDownload();
        this.rightMovie = data.getRights().getMovie();
        this.rightPay = data.getRights().getPay();
        this.rightHd5 = data.getRights().getHd5();
        this.rightNoReprint = data.getRights().getNo_reprint();
        this.rightAutoplay = data.getRights().getAutoplay();
        this.rightUgcPay = data.getRights().getUgc_pay();
        this.rightIsCooperation = data.getRights().getIs_cooperation();
        this.rightUgcPayPreview = data.getRights().getUgc_pay_preview();
        this.rightNoBackground = data.getRights().getNo_background();
        this.dimensionWidth = data.getDimension().getWidth();
        this.dimensionHeight = data.getDimension().getHeight();
        this.dimensionRotate = data.getDimension().getRotate();
        this.lastUpdateTime = new DateTime(DateTimeZone.forOffsetHours(8)).toDate();
    }

    @TableId private Long aid;

    private Integer videos;

    private Integer tid;

    private String tname;

    private Integer copyright;

    private String pic;

    private String title;

    private Date pubdate;

    private Date ctime;

    @TableField("`desc`")
    private String desc;

    private Integer state;

    private Integer attribute;

    private Integer duration;

    private Long missionId;

    private String dynamic;

    private Long cid;

    private String bvid;

    /** 关联用户表 */
    private Long ownerMid;

    /** 关联stat表 */
    private Long statAid;

    private Byte rightBp;

    private Byte rightElec;

    private Byte rightDownload;

    private Byte rightMovie;

    private Byte rightPay;

    private Byte rightHd5;

    private Byte rightNoReprint;

    private Byte rightAutoplay;

    private Byte rightUgcPay;

    private Byte rightIsCooperation;

    private Byte rightUgcPayPreview;

    private Byte rightNoBackground;

    private Integer dimensionWidth;

    private Integer dimensionHeight;

    private Byte dimensionRotate;

    private Date lastUpdateTime;

    private Date createTime;
}
