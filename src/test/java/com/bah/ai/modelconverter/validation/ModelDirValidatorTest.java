package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ModelDirValidatorTest {
    Map<AppVariable, String> validModelDirConfig = new HashMap<AppVariable, String>() {{
        put(AppVariable.MODEL_DIR, "src/resources/yolo");
    }};

    Map<AppVariable, String> missingModelDirConfig = new HashMap<AppVariable, String>();

    ModelDirValidator modelDirV = new ModelDirValidator();

    @Test
    void testValidModelDir() {
        boolean valid = modelDirV.validate(validModelDirConfig);
        assertTrue(valid);
    }

    @Test
    void testInvalidModelDir() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> modelDirV.validate(missingModelDirConfig));
    }
}