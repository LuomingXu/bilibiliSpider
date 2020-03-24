package bilibilispider.multiprocess.online;

import com.fasterxml.jackson.core.json.JsonReadFeature;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.joda.time.DateTime;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.annotation.Transient;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service("onlineAnalyze")
public class Analyze {
    @Autowired private AvInfoServiceI infoService;
    @Autowired private AvStatServiceI statService;

    @Transient
    public void main(String json, DateTime createTime) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.enable(JsonReadFeature.ALLOW_UNESCAPED_CONTROL_CHARS.mappedFeature());
        JsonNode j = objectMapper.readTree(json);
        List<OnlineData> dataList =
                objectMapper.readValue(
                        j.findValue("onlineList").toString(), new TypeReference<>() {});
        dataList.sort((f, s) -> s.getOnline_count().compareTo(f.getOnline_count()));

        int i = 0;
        for (OnlineData item : dataList) {
            AvInfo info = new AvInfo(item);
            AvStat stat = new AvStat(item, (byte) ++i, createTime);
            AvInfo exist = infoService.lambdaQuery().eq(AvInfo::getAid, item.getAid()).one();
            if (exist == null) {
                log.info("[Insert] aid: {}", item.getAid());
                if (infoService.save(info)) {
                    log.info("[Insert] av info success");
                } else {
                    log.error("[Insert] av info failed");
                    throw new Exception();
                }
            } else {
                log.info("[Update] aid: {}", item.getAid());
            }
            if (statService.save(stat)) {
                log.info("[Insert] av stat success");
            } else {
                log.error("[Insert] av stat failed");
                throw new Exception();
            }
        }
    }
}
