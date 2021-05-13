package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class S3VerifierTest {
    Map<String, String> validCredentials = new HashMap<String, String>() {{
        put("USER_ACCESS_KEY", "AKIAUX272I2XL6D3MX7N");
        put("USER_SECRET_KEY", "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");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
    }};

    Map<String, String> validBucketNonValidCreds = new HashMap<String, String>() {{
        put("USER_ACCESS_KEY", "KKKKK");
        put("USER_SECRET_KEY", "ZZZZZ");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
    }};

    Map<String, String> validCredsNonValidBucket = new HashMap<String, String>() {{
        put("USER_ACCESS_KEY", "AKIAUX272I2XL6D3MX7N");
        put("USER_SECRET_KEY", "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");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "whatever");
    }};

    Map<String, String> nonValidCredsBucket = new HashMap<String, String>() {{
        put("USER_ACCESS_KEY", "xxxx");
        put("USER_SECRET_KEY", "yyyy");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "whatever");
    }};

    Map<String, String> emptySettings = new HashMap<>();

    S3Verifier s3Verifier = new S3Verifier();

    @Test
    public void testValidS3Access() {
        s3Verifier.verify(validCredentials);
        assertNull(s3Verifier.failureReason);
    }

    @Test
    public void testNotValidCredsWithValidBucket() {
        s3Verifier.verify(validBucketNonValidCreds);
        assertNotNull(s3Verifier.failureReason);
    }

    @Test
    public void testValidCredsWithNonValidBucket() {
        s3Verifier.verify(validCredsNonValidBucket);
        assertNotNull(s3Verifier.failureReason);
    }

    @Test
    public void testValidCredsAndBucket() {
        s3Verifier.verify(nonValidCredsBucket);
        assertNotNull(s3Verifier.failureReason);
    }

    @Test
    public void testEmptySettings() {
        s3Verifier.verify(emptySettings);
        assertNotNull(s3Verifier.failureReason);
    }
}
