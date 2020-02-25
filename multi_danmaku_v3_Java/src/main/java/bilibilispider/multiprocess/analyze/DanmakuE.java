package bilibilispider.multiprocess.analyze;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.util.Date;

@Data
@TableName("danmaku")
public class DanmakuE {
    @TableId private Long id;

    private Integer mode;

    private Integer fontSize;

    private Integer fontColor;

    private Date sendTime;

    private Integer danmakuPool;

    private Double danmakuEpoch;

    private Long userHash;

    private Long userId = -1L;

    private String content;
}
