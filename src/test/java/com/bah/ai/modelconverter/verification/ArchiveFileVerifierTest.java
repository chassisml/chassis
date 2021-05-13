package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import com.bah.ai.modelconverter.dto.AssetVerifierDTO;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ArchiveFileVerifierTest {
    ArchiveFileVerifier archiveFileVerifier;

    Map<String, String> validArchive = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
        put("ASSET_PATH", "weights/saumil_resource_archive.tar.gz");
    }};

    Map<String, String> nonValidArchive = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
        put("ASSET_PATH", "weights/test.txt");
    }};

    Map<String, String> nonExistingBucket = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "whatever");
        put("ASSET_PATH", "weights/test.txt");
    }};

    Map<String, String> nonExistingArchive = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
        put("ASSET_PATH", "weights/yyyyy.txt");
    }};

    Map<String, String> missingDesc = new HashMap<String, String>() {{
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
        put("ASSET_PATH", "weights/saumil_resource_archive.tar.gz");
    }};

    Map<String, String> missingBucket = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put("ASSET_PATH", "weights/saumil_resource_archive.tar.gz");
    }};

    Map<String, String> missingPath = new HashMap<String, String>() {{
        put("ASSET_DESC", "Testing archive");
        put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
    }};

    Map<String, String> emptySettings = new HashMap<String, String>();

    public ArchiveFileVerifierTest() {
        AssetVerifierDTO s3VerifierDTO = new AssetVerifierDTO();
        s3VerifierDTO.setVerifierObj(new S3Verifier());
        s3VerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("USER_ACCESS_KEY", "AKIAUX272I2XL6D3MX7N");
            put("USER_SECRET_KEY", "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");
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), "sagemaker-testing-ds");
        }});
        s3VerifierDTO.getVerifierObj().verify(s3VerifierDTO.getVerifierSettings());

        archiveFileVerifier = new ArchiveFileVerifier("PARAMS", s3VerifierDTO.getVerifierObj(), new File("src/tmp"));
    }

    @Test
    public void testValidArchive() {
        archiveFileVerifier.verify(validArchive);
        assertNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testNonValidArchive() {
        archiveFileVerifier.verify(nonValidArchive);
        assertNotNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testNonExistingBucket() {
        archiveFileVerifier.verify(nonExistingBucket);
        assertNotNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testNonExistingArchive() {
        archiveFileVerifier.verify(nonExistingArchive);
        assertNotNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testMissingDescription() {
        archiveFileVerifier.verify(missingDesc);
        assertNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testMissingBucket() {
        archiveFileVerifier.verify(missingBucket);
        assertNotNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testMissingPath() {
        archiveFileVerifier.verify(missingPath);
        assertNotNull(archiveFileVerifier.failureReason);
    }

    @Test
    public void testEmptySettings() {
        archiveFileVerifier.verify(emptySettings);
        assertNotNull(archiveFileVerifier.failureReason);
    }
}
