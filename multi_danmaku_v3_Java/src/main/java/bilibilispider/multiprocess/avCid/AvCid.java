package bilibilispider.multiprocess.avCid;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("av_cids")
public class AvCid
{
    @TableId
    private Long cid;

    private Integer page;

    @TableField(value = "page_name")
    private String pagename;

    private Long aid;
}
