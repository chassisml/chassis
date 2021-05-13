package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ImporterTest {
    Map<AppVariable, String> importerValidConfig = new HashMap<AppVariable, String>() {{
        put(AppVariable.IMPORTER_HOST, "xxx.yyy.com");
        put(AppVariable.IMPORTER_PORT, "2020");
    }};

    Map<AppVariable, String> importerValidOnlyHost = new HashMap<AppVariable, String>() {{
        put(AppVariable.IMPORTER_HOST, "xxx.yyy.com");
    }};

    Map<AppVariable, String> importerInvalidOnlyPort = new HashMap<AppVariable, String>() {{
        put(AppVariable.IMPORTER_PORT, "2021");
    }};

    Map<AppVariable, String> emptyImporterConfig = new HashMap<AppVariable, String>();

    ImporterValidator importerValidator = new ImporterValidator();

    @Test
    void testValidImporter() {
        boolean valid = importerValidator.validate(importerValidConfig);
        assertTrue(valid);
    }

    @Test
    void testValidImporterOnlyHost() {
        boolean valid = importerValidator.validate(importerValidOnlyHost);
        assertTrue(valid);
    }

    @Test
    void testInvalidImporterOnlyPort() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> importerValidator.validate(importerInvalidOnlyPort));
    }

    @Test
    void testInvalidWhenEmptySettings() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class, () -> importerValidator.validate(emptyImporterConfig));
    }
}
