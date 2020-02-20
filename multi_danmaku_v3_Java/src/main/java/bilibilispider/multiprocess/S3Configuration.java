package bilibilispider.multiprocess;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;

@Data
@ConfigurationProperties(prefix = S3Configuration.PREFIX)
public class S3Configuration implements AWSCredentialsProvider {
    public static final String PREFIX = "s3";

    private String endpoint;

    private String region;

    private String bucket;

    private String accessKey;

    private String secretKey;

    private String tempFileDir;

    private Integer cpuUseNumber;

    @Bean(name = {"amazonS3"})
    public AmazonS3 amazonS3() {
        return AmazonS3ClientBuilder.standard()
                .withCredentials(this)
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                this.getEndpoint(), this.region))
                .build();
    }

    @Override
    public AWSCredentials getCredentials() {
        return new BasicAWSCredentials(
                this.accessKey, this.secretKey);
    }

    @Override
    public void refresh() {}
}
