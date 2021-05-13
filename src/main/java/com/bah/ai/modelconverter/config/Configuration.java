package com.bah.ai.modelconverter.config;

import lombok.Data;

import java.util.Date;

import static java.lang.String.format;

@Data
public final class Configuration {
    private Date released;
    private String version;
    private String resourceDir;
    private String workingDir;
    private String importerResDir;
    private String importerRootDir;
    private String importerModelDir;
    private String modelScriptDir;
    private int kanikoWaitTime;
    private int kanikoTimeout;
    private String modelConfigName;
    private String modelFileName;
    private String paramsDirName;
    private String otherResDirName;

    @Override
    public String toString() {
        return new StringBuilder()
                .append(format("Version: %s\n", version))
                .append(format("Released: %s\n", released))
                .append(format("Resource directory: %s\n", resourceDir))
                .append(format("Work directory: %s\n", workingDir))
                .append(format("Resources directory for importer: %s\n", importerResDir))
                .append(format("Root directory for importer: %s\n", importerRootDir))
                .append(format("Model directory of importer: %s\n", importerModelDir))
                .append(format("Container directory of model script: %s\n", modelScriptDir))
                .append(format("Kaniko image wait time: %s\n", kanikoWaitTime))
                .append(format("Kaniko minutes for timeout: %s\n", kanikoTimeout))
                .append(format("Model config file name: %s\n", modelConfigName))
                .append(format("Model file name: %s\n", modelFileName))
                .append(format("Parameters directory name: %s\n", paramsDirName))
                .append(format("Other resources directory name: %s\n", otherResDirName))
                .toString();
    }
}
