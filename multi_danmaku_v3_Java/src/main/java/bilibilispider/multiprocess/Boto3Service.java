package bilibilispider.multiprocess;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.*;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Slf4j
@Service
public class Boto3Service {
    @Autowired private AmazonS3 amazonS3;

    @Autowired private S3Configuration config;

    public Set<String> getAllObjects() {
        Set<String> objects = new HashSet<>();
        ListObjectsRequest request = new ListObjectsRequest();

        request.setBucketName(config.getBucket());

        while (true) {
            ObjectListing res = amazonS3.listObjects(request);
            for (S3ObjectSummary item : res.getObjectSummaries()) {
                objects.add(item.getKey());
            }
            if (!res.isTruncated()) {
                break;
            } else {
                log.info("[s3] Got {} keys", objects.size());
                request.setMarker(res.getNextMarker());
            }
        }

        log.info("[s3] {} total keys", objects.size());
        return objects;
    }

    public void downloadObjects(Set<String> objects) throws InterruptedException
    {
        Map<String, InputStream> map = new HashMap<>();
        Thread thread;
        int count = 0;
        for (String key : objects) {
            count++;
            S3Object object = amazonS3.getObject(config.getBucket(), key);
            S3ObjectInputStream stream = object.getObjectContent();
            map.put(config.getTempFileDir() + "/" + key, stream.getDelegateStream());
            if (map.size() % 50 == 0) {
                log.info("[s3] download 50");
                thread = new Thread(new MultiDownload(map));
                thread.start();
                map = new HashMap<>();
            }
        }
        thread = new Thread(new MultiDownload(map));
        thread.start();
        thread.join();
    }

    static class MultiDownload implements Runnable {
        private Map<String, InputStream> map;

        public MultiDownload(Map<String, InputStream> map) {
            this.map = map;
        }

        @SneakyThrows
        @Override
        public void run() {
            for (Map.Entry<String, InputStream> entry : map.entrySet()) {
                File dir = new File(entry.getKey()).getParentFile();
                if (!dir.exists()) {
                    dir.mkdirs();
                }
                FileOutputStream fos = new FileOutputStream(entry.getKey());
                byte[] read_buffer = new byte[1024];
                int read_len = 0;
                while ((read_len = entry.getValue().read(read_buffer)) > 0) {
                    fos.write(read_buffer, 0, read_len);
                }

                fos.close();
                entry.getValue().close();
            }
        }
    }
}
