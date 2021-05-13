package com.bah.ai.modelconverter.verification;


import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static com.github.stefanbirkner.systemlambda.SystemLambda.withEnvironmentVariable;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ECRVerifierTest {
    Map<String, String> ecrValidSetting = new HashMap<String, String>() {{
        put(AppVariable.ECR_REPO.getAppVarName(), "sagemaker-testing");
    }};

    Map<String, String> ecrNonValidSetting = new HashMap<String, String>() {{
        put(AppVariable.ECR_REPO.getAppVarName(), "whatever_registry");
    }};

    Map<String, String> emptySetting = new HashMap<String, String>();

    ECRVerifier ecrVerifier = new ECRVerifier();

    @Test
    public void testValidECRSettings() throws Exception {
        withEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .execute(() -> ecrVerifier.verify(ecrValidSetting));
        assertNull(ecrVerifier.getFailureReason());
    }

    @Test
    public void testNonValidECRSettings() throws Exception {
        withEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .execute(() -> ecrVerifier.verify(ecrNonValidSetting));
        assertNotNull(ecrVerifier.getFailureReason());
    }

    @Test
    public void testEmptyECRSettings() throws Exception {
        withEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .execute(() -> ecrVerifier.verify(emptySetting));
        assertNotNull(ecrVerifier.getFailureReason());
    }
}
