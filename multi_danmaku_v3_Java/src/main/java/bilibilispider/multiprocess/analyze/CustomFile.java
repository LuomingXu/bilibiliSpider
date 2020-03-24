package bilibilispider.multiprocess.analyze;

import lombok.Data;
import org.joda.time.DateTime;

@Data
public class CustomFile {
    private String fileName;

    private FileType fileType;

    private String content;

    private DateTime createTime;

    private Long aid;

    private Long cid;

    public enum FileType {
        Online,
        Danmaku,
        AvCids
    }
}
