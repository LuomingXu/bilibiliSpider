package bilibilispider.multiprocess.avCid;

import com.fasterxml.jackson.core.json.JsonReadFeature;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.annotation.Transient;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service("avCidAnalyze")
public class Analyze {
    @Autowired private AvCidServiceI service;

    @Transient
    public void main(String json, Long aid) throws Exception {
        List<AvCid> res = service.lambdaQuery().eq(AvCid::getAid, aid).list();
        if (res != null && res.size() > 0) {
            return;
        }

        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.enable(JsonReadFeature.ALLOW_UNESCAPED_CONTROL_CHARS.mappedFeature());
        List<AvCid> dataList = objectMapper.readValue(json, new TypeReference<>() {});
        dataList.forEach(item -> item.setAid(aid));
        if (service.saveBatch(dataList)) {
            log.info("[Av->Cids] Saved, aic: {}", aid);
        } else {
            log.error("[Av->Cids] Failed, aic: {}", aid);
            throw new Exception();
        }
    }
}
