package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ModelTypeValidatorTest {
    Map<AppVariable, String> validSetting = new HashMap<AppVariable, String>() {{
        put(AppVariable.MODEL_TYPE, "resnet");
    }};

    Map<AppVariable, String> emptyConfig = new HashMap<AppVariable, String>();

    ModelTypeValidator modelTypeValidator = new ModelTypeValidator();

    @Test
    void testValidECR() {
        boolean valid = modelTypeValidator.validate(validSetting);
        assertTrue(valid);
    }

    @Test
    void testInvalidWhenEmptySettings() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> modelTypeValidator.validate(emptyConfig));
    }
}
