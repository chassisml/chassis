package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ModelTypeVerifierTest {
    Map<String, String> validModelType = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "src/resources");
        put(AppVariable.MODEL_TYPE.getAppVarName(), "image-classification");
    }};

    Map<String, String> nonValidDir = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "abc/resources");
        put(AppVariable.MODEL_TYPE.getAppVarName(), "image-classification");
    }};

    Map<String, String> nonValidType = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "src/resources");
        put(AppVariable.MODEL_TYPE.getAppVarName(), "computer-vision");
    }};

    Map<String, String> nonValidModelTypeSettings = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "abc/resources");
        put(AppVariable.MODEL_TYPE.getAppVarName(), "computer-vision");
    }};

    Map<String, String> missingDirSetting = new HashMap<String, String>() {{
        put(AppVariable.MODEL_TYPE.getAppVarName(), "image-classification");
    }};

    Map<String, String> missingTypeSetting = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "src/resources");
    }};

    Map<String, String> emptySettings = new HashMap<String, String>();

    ModelTypeVerifier modelTypeVerifier = new ModelTypeVerifier();


    @Test
    public void testValidModelType() {
        modelTypeVerifier.verify(validModelType);
        assertNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testNonValidDir() {
        modelTypeVerifier.verify(nonValidDir);
        assertNotNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testNonValidType() {
        modelTypeVerifier.verify(nonValidType);
        assertNotNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testNonValidSettings() {
        modelTypeVerifier.verify(nonValidModelTypeSettings);
        assertNotNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testMissingDirSettings() {
        modelTypeVerifier.verify(missingDirSetting);
        assertNotNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testMissingTypeSettings() {
        modelTypeVerifier.verify(missingTypeSetting);
        assertNotNull(modelTypeVerifier.failureReason);
    }

    @Test
    public void testEmptySettings() {
        modelTypeVerifier.verify(emptySettings);
        assertNotNull(modelTypeVerifier.failureReason);
    }
}
