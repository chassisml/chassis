package com.bah.ai.modelconverter.verification;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.Bucket;
import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class S3Verifier extends AssetVerifier<AmazonS3> {
    public S3Verifier() {
        this.assetName = "S3";
    }

    public boolean verify(Map<String, String> parameters) {
        boolean verified = false;
        String userS3Access = parameters.get("USER_ACCESS_KEY");
        String userS3Secret = parameters.get("USER_SECRET_KEY");
        String userBucketName = parameters.get(AppVariable.SAGEMAKER_BUCKET.getAppVarName());
        Region region = Regions.getCurrentRegion() != null ? Regions.getCurrentRegion() : Region.getRegion(Regions.US_EAST_1);
        try {
            BasicAWSCredentials credentials = new BasicAWSCredentials(userS3Access, userS3Secret);
            this.asset = AmazonS3ClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .withRegion(region.getName())
                    .build();
            for (Bucket b : this.asset.listBuckets()) {
                if (b.getName().equals(userBucketName)) {
                    verified = true;
                    log.info("Access to S3 verified and ready for usage in next steps");
                    break;
                }
            }

            if (!verified) {
                this.failureReason = String.format("Access to S3 may be verified but the bucket, %sis not present under this user profile", userBucketName);
                log.error(this.failureReason);
            }
        } catch (Exception e) {
            this.failureReason = e.getMessage();
            log.error("Error while trying to get access to S3, verify that your AWS keys or profile has access to this service.", e);
        }

        return verified;
    }
}
