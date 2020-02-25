package bilibilispider.multiprocess;

import bilibilispider.multiprocess.analyze.Analyze;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

import java.io.File;
import java.util.Objects;

@EnableConfigurationProperties(S3Configuration.class)
@SpringBootApplication
public class Main implements CommandLineRunner {
    @Autowired private Boto3Service boto3Service;
    @Autowired private S3Configuration config;
    @Autowired private Analyze analyze;

    public static void main(String[] args) {
        SpringApplication.run(Main.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        // todo download

        File file = new File(config.getTempFileDir());
        for (File item : Objects.requireNonNull(file.listFiles())) {
            analyze.main(item.getPath());
        }
    }
}
