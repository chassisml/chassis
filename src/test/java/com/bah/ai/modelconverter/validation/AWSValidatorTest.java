package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class AWSValidatorTest {
    Map<AppVariable, String> validAWSSettings = new HashMap<AppVariable, String>() {{
        put(AppVariable.AWS_KEY_ID, "ZZZ");
        put(AppVariable.AWS_SECRET_KEY, "YYY");
    }};

    Map<AppVariable, String> missingKeyId = new HashMap<AppVariable, String>() {{
        put(AppVariable.AWS_SECRET_KEY, "YYY");
    }};

    Map<AppVariable, String> missingSecretKey = new HashMap<AppVariable, String>() {{
        put(AppVariable.AWS_KEY_ID, "ZZZ");
    }};

    Map<AppVariable, String> emptySettings = new HashMap<AppVariable, String>();

    AWSValidator awsValidator = new AWSValidator();

    @Test
    void testValidSettings() {
        boolean valid = awsValidator.validate(validAWSSettings);
        assertTrue(valid);
    }

    @Test
    void testInvalidWhenMissingKey() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> awsValidator.validate(missingKeyId));
    }

    @Test
    void testInvalidWhenMissingSecret() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> awsValidator.validate(missingSecretKey));
    }

    @Test
    void testInvalidWhenEmptySettings() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> awsValidator.validate(emptySettings));
    }
}
