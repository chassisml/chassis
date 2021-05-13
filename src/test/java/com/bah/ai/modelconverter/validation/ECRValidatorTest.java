package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ECRValidatorTest {
    Map<AppVariable, String> validECRConfig = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REGISTRY, "ZZZ");
        put(AppVariable.ECR_REPO, "YYY");
        put(AppVariable.ECR_USER, "XXX");
    }};

    Map<AppVariable, String> missingECRUser = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REGISTRY, "ZZZ");
        put(AppVariable.ECR_REPO, "YYY");
    }};

    Map<AppVariable, String> missingECRRepo = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REGISTRY, "ZZZ");
        put(AppVariable.ECR_USER, "XXX");
    }};

    Map<AppVariable, String> missingECRRegistry = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REPO, "YYY");
        put(AppVariable.ECR_USER, "XXX");
    }};

    Map<AppVariable, String> onlyRegistry = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REGISTRY, "ZZZ");
    }};

    Map<AppVariable, String> onlyRepo = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_REPO, "YYY");
    }};

    Map<AppVariable, String> onlyUser = new HashMap<AppVariable, String>() {{
        put(AppVariable.ECR_USER, "XXX");
    }};

    Map<AppVariable, String> emptyECRConfig = new HashMap<AppVariable, String>();

    ECRValidator ecrValidator = new ECRValidator();

    @Test
    void testValidECR() {
        boolean valid = ecrValidator.validate(validECRConfig);
        assertTrue(valid);
    }

    @Test
    void testMissingECRUser() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(missingECRUser));
    }

    @Test
    void testMissingECRRepo() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(missingECRRepo));
    }

    @Test
    void testMissingECRRegistry() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(missingECRRegistry));
    }

    @Test
    void testInvalidWhenOnlyRegistry() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(onlyRegistry));
    }

    @Test
    void testInvalidWhenOnlyRepo() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(onlyRepo));
    }

    @Test
    void testInvalidWhenOnlyUser() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(onlyUser));
    }

    @Test
    void testInvalidWhenEmptySettings() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> ecrValidator.validate(emptyECRConfig));
    }
}
