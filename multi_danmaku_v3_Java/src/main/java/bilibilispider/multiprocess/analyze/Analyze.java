package bilibilispider.multiprocess.analyze;

import bilibilispider.multiprocess.S3Configuration;
import bilibilispider.multiprocess.Serialize;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.text.StringEscapeUtils;
import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

@Slf4j
@Service("analyze")
@SuppressWarnings("unchecked")
public class Analyze {
    @Autowired private S3Configuration config;
    @Autowired private bilibilispider.multiprocess.online.Analyze onlineAnalyze;
    @Autowired private bilibilispider.multiprocess.avCid.Analyze avCidAnalyze;

    public void main(String path) throws Exception {
        int cpu_use_number = config.getCpuUseNumber();

        // read all files in "path"
        List<File> files = readAllFiles(path, new ArrayList<>());
        Map<String, CustomFile> customFiles = classifyFiles(files);

        // deconstruct Filetype.danmaku
        long count =
                customFiles.values().stream()
                        .filter(item -> item.getFileType().equals(CustomFile.FileType.Danmaku))
                        .count();
        int size = (int) (Math.ceil((double) count / cpu_use_number));

        ExecutorService pool = Executors.newWorkStealingPool(cpu_use_number);
        Map<String, CustomFile> tempFileMap = new HashMap<>();
        List<Future<DeconstructE>> futures = new ArrayList<>();
        for (Map.Entry<String, CustomFile> item : customFiles.entrySet()) {
            CustomFile file = item.getValue();

            switch (file.getFileType()) {
                case AvCids:
                    avCidAnalyze.main(file.getContent(), file.getAid());
                    break;
                case Online:
                    onlineAnalyze.main(file.getContent(), file.getCreateTime());
                    break;
                case Danmaku:
                    tempFileMap.put(item.getKey(), file);
                    if (tempFileMap.size() == size) {
                        futures.add(pool.submit(new Deconstruct(tempFileMap)));
                        tempFileMap = new HashMap<>();
                    }
                    break;
                default:
                    break;
            }
        }
        futures.add(pool.submit(new Deconstruct(tempFileMap)));

        while (true) {
            long completedCount = futures.stream().filter(Future::isDone).count();
            if (completedCount == futures.size()) {
                log.info("Deconstruct danmakus completed.");
                break;
            }
            Thread.sleep(1000);
        }

        List<DanmakuE> danmakuES = new ArrayList<>();
        Map<Long, Set<Long>> cidDanmakuIds = new HashMap<>();
        for (Future<DeconstructE> item : futures) {
            danmakuES.addAll(item.get().getDanmakus());
            cidDanmakuIds.putAll(item.get().getCidDanmakuIds());
        }

        serializeDanmakus(path + ".danmaku", danmakuES, cidDanmakuIds);
    }

    public Map<String, CustomFile> classifyFiles(List<File> files) throws IOException {
        Map<String, CustomFile> customFiles = new HashMap<>();
        for (File item : files) {
            String[] fullFileName = item.getName().split("\\.");
            String fileName = fullFileName[0];
            String extension = fullFileName[1];

            if (extension.equals("xml")) {
                String[] arr = fileName.split("-");
                CustomFile temp = new CustomFile();
                temp.setFileName(item.getName());
                temp.setContent(
                        Files.readString(Paths.get(item.getPath()), StandardCharsets.UTF_8));
                temp.setFileType(CustomFile.FileType.Danmaku);
                temp.setCreateTime(
                        new DateTime(
                                Long.parseLong(arr[2]) / 1000000000,
                                DateTimeZone.forOffsetHours(8)));
                temp.setAid(Long.valueOf(arr[0]));
                temp.setCid(Long.valueOf(arr[1]));
                customFiles.put(fileName, temp);
            }
            if (extension.equals("json")) {
                if (item.getParentFile().getName().equals("online")) {
                    CustomFile temp = new CustomFile();
                    temp.setFileName(fileName);
                    temp.setContent(
                            StringEscapeUtils.unescapeJson(
                                    Files.readString(
                                            Paths.get(item.getPath()), StandardCharsets.UTF_8)));
                    temp.setCreateTime(
                            new DateTime(
                                    Long.parseLong(fileName) / 1000000000,
                                    DateTimeZone.forOffsetHours(8)));
                    temp.setFileType(CustomFile.FileType.Online);
                    customFiles.put(fileName, temp);
                } else if (item.getParentFile().getName().equals("danmaku")) {
                    CustomFile temp = new CustomFile();
                    temp.setFileName(fileName);
                    temp.setContent(
                            StringEscapeUtils.unescapeJson(
                                    Files.readString(
                                            Paths.get(item.getPath()), StandardCharsets.UTF_8)));
                    temp.setAid(Long.valueOf(fileName));
                    temp.setFileType(CustomFile.FileType.AvCids);
                    customFiles.put(fileName, temp);
                }
            }
        }

        return customFiles;
    }

    /** read all files in specific dir */
    public List<File> readAllFiles(String path, List<File> files) {
        File file = new File(path);
        for (File item : Objects.requireNonNull(file.listFiles())) {
            if (item.getName().equals("package-info.java")) {
                continue; // do not read placeholder file
            }
            if (item.isFile()) {
                files.add(item);
            } else {
                readAllFiles(item.getPath(), files);
            }
        }

        return files;
    }

    public void serializeDanmakus(String fileName, List<DanmakuE> list, Map<Long, Set<Long>> map)
            throws Exception {
        Serialize.Msg.Builder msgBuilder = Serialize.Msg.newBuilder();
        Serialize.Msg.DanmakuP.Builder builder;
        List<Serialize.Msg.DanmakuP> l = new ArrayList<>();
        for (DanmakuE item : list) {
            builder = Serialize.Msg.DanmakuP.newBuilder();
            builder.setContent(item.getContent());
            builder.setDanmakuEpoch(item.getDanmakuEpoch());
            builder.setDanmakuPool(item.getDanmakuPool());
            builder.setFontColor(item.getFontColor());
            builder.setFontSize(item.getFontSize());
            builder.setId(item.getId());
            builder.setUserHash(item.getUserHash());
            builder.setUserId(item.getUserId());
            builder.setSendTime(item.getSendTime().getTime());
            l.add(builder.build());
        }

        Serialize.Msg.DanmakuMap.Builder mapBuilder;
        List<Serialize.Msg.DanmakuMap> m = new ArrayList<>();
        for (Map.Entry<Long, Set<Long>> item : map.entrySet()) {
            mapBuilder = Serialize.Msg.DanmakuMap.newBuilder();
            mapBuilder.setCid(item.getKey());
            mapBuilder.addAllDanmakuId(item.getValue());
            m.add(mapBuilder.build());
        }

        msgBuilder.addAllCidDanmakuIds(m);
        Serialize.Msg msg = msgBuilder.addAllDanmakus(l).build();

        msg.writeTo(new FileOutputStream(new File(fileName)));
    }

    public void saveAidCidRealation(String path, Map<Long, Set<Long>> map) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(map);
        FileUtils.write(new File(path), json, StandardCharsets.UTF_8);
    }

    public DeconstructE deserializeDanmakus(String path) throws Exception {
        DeconstructE res = new DeconstructE();

        Serialize.Msg msg = Serialize.Msg.parseFrom(new FileInputStream(path));
        List<DanmakuE> l = new ArrayList<>();
        for (Serialize.Msg.DanmakuP item : msg.getDanmakusList()) {
            DanmakuE obj = new DanmakuE();
            obj.setContent(item.getContent());
            obj.setDanmakuEpoch(item.getDanmakuEpoch());
            obj.setDanmakuPool(item.getDanmakuPool());
            obj.setFontColor(item.getFontColor());
            obj.setFontSize(item.getFontSize());
            obj.setId(item.getId());
            obj.setUserHash(item.getUserHash());
            obj.setUserId(item.getUserId());
            obj.setSendTime(
                    new DateTime(item.getSendTime(), DateTimeZone.forOffsetHours(8)).toDate());
            l.add(obj);
        }
        res.setDanmakus(l);

        Map<Long, Set<Long>> map = new HashMap<>();
        for (Serialize.Msg.DanmakuMap item : msg.getCidDanmakuIdsList()) {
            Set<Long> value = map.computeIfAbsent(item.getCid(), k -> new HashSet<>());
            value.addAll(item.getDanmakuIdList());
        }

        res.setCidDanmakuIds(map);
        return res;
    }

    /** 这边读取返回的时候key会变成String */
    public Map<Long, Set<Long>> readAidCidRealation(String path) throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String json = FileUtils.readFileToString(new File(path), StandardCharsets.UTF_8);
        return objectMapper.readValue(json, Map.class);
    }

    public Integer usedMemory() {
        return (int)
                (ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed() / 1024 / 1024);
    }

    static class Deconstruct implements Callable<DeconstructE> {
        private Map<String, CustomFile> fileMap;

        public Deconstruct(Map<String, CustomFile> fileMap) {
            this.fileMap = fileMap;
        }

        @Override
        public DeconstructE call() throws Exception {
            DeconstructE res = new DeconstructE();
            List<DanmakuE> danmakus = new ArrayList<>();
            Map<Long, Set<Long>> map = new HashMap<>();

            for (Map.Entry<String, CustomFile> item : fileMap.entrySet()) {
                Set<Long> set = map.get(item.getValue().getCid());
                if (set == null) {
                    set = new HashSet<>();
                }

                try {
                    Document document = DocumentHelper.parseText(item.getValue().getContent());

                    for (Element elem : document.getRootElement().elements()) {
                        if (elem.getQName().getName().equals("d")) {
                            // 弹幕出现时间,模式,字体大小,颜色,发送时间戳,弹幕池,用户Hash,数据库ID
                            DanmakuE entity = new DanmakuE();
                            String[] l = elem.attribute("p").getValue().split(",");
                            entity.setDanmakuEpoch(Double.valueOf(l[0]));
                            entity.setMode(Integer.valueOf(l[1]));
                            entity.setFontSize(Integer.valueOf(l[2]));
                            entity.setFontColor(Integer.valueOf(l[3]));
                            entity.setSendTime(
                                    new DateTime(Long.valueOf(l[4]), DateTimeZone.forOffsetHours(8))
                                            .toDate());
                            entity.setDanmakuPool(Integer.valueOf(l[5]));
                            entity.setUserHash(Long.parseLong(l[6], 16));
                            entity.setId(Long.valueOf(l[7]));

                            entity.setContent(elem.getStringValue());

                            danmakus.add(entity);
                            set.add(entity.getId());
                        }
                    }
                } catch (Exception e) {
                    log.info(item.getKey());
                    e.printStackTrace();
                    System.exit(0);
                }
                map.put(item.getValue().getCid(), set);
            }

            res.setDanmakus(danmakus);
            res.setCidDanmakuIds(map);
            return res;
        }
    }
}
