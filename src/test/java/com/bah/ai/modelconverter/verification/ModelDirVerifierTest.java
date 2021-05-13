package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ModelDirVerifierTest {
    Map<String, String> validSetting = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "src/resources");
    }};

    Map<String, String> nonValidSetting = new HashMap<String, String>() {{
        put(AppVariable.MODEL_DIR.getAppVarName(), "abc/resources");
    }};

    Map<String, String> emptySetting = new HashMap<String, String>();

    ModelDirVerifier modelDirVerifier = new ModelDirVerifier();

    @Test
    public void testValidModelDir() {
        modelDirVerifier.verify(validSetting);
        assertNull(modelDirVerifier.failureReason);
    }

    @Test
    public void testNonValidModelDir() {
        modelDirVerifier.verify(nonValidSetting);
        assertNotNull(modelDirVerifier.failureReason);
    }

    @Test
    public void testEmptyModelDir() {
        modelDirVerifier.verify(emptySetting);
        assertNotNull(modelDirVerifier.failureReason);
    }
}
