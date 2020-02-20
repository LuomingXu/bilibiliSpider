package bilibilispider.multiprocess;

import lombok.Data;

import java.util.List;
import java.util.Map;
import java.util.Set;

@Data
public class DeconstructE
{
    private List<DanmakuE> danmakus;

    private Map<Integer, Set<Long>> cidDanmakuIds;
}
