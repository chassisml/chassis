package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

public class ImporterVerifierTest {
    Map<String, String> validImporterSettings = new HashMap<String, String>() {{
        put(AppVariable.IMPORTER_HOST.getAppVarName(), "localhost");
    }};

    Map<String, String> nonValidImporterPort = new HashMap<String, String>() {{
        put(AppVariable.IMPORTER_HOST.getAppVarName(), "localhost");
        put(AppVariable.IMPORTER_PORT.getAppVarName(), "8081");
    }};

    Map<String, String> nonValidImporterHost = new HashMap<String, String>() {{
        put(AppVariable.IMPORTER_HOST.getAppVarName(), "www.autocv.com");
    }};

    Map<String, String> nonValidSettings = new HashMap<String, String>() {{
        put(AppVariable.IMPORTER_HOST.getAppVarName(), "www.autocv.com");
        put(AppVariable.IMPORTER_PORT.getAppVarName(), "2025");
    }};

    Map<String, String> emptySettings = new HashMap<String, String>();

    ImporterVerifier importerVerifier = new ImporterVerifier();

    @Test
    public void testValidImporterSettings() {
        importerVerifier.verify(validImporterSettings);
        assertNull(importerVerifier.failureReason);
    }

    @Test
    public void testNonValidImporterPort() {
        importerVerifier.verify(nonValidImporterPort);
        assertNotNull(importerVerifier.failureReason);
    }

    @Test
    public void testNonValidImporterHost() {
        importerVerifier.verify(nonValidImporterHost);
        assertNotNull(importerVerifier.failureReason);
    }

    @Test
    public void testNonValidSettings() {
        importerVerifier.verify(nonValidSettings);
        assertNotNull(importerVerifier.failureReason);
    }

    @Test
    public void testEmptySettings() {
        importerVerifier.verify(emptySettings);
        assertNotNull(importerVerifier.failureReason);
    }

}
