package com.bah.ai.modelconverter.config;

import static java.lang.String.format;

public class AssetConfig {
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getLastVersion() {
        return lastVersion;
    }

    public void setLastVersion(String lastVersion) {
        this.lastVersion = lastVersion;
    }

    public DockerRepository getDockerRepository() {
        return dockerRepository;
    }

    public void setDockerRepository(DockerRepository dockerRepository) {
        this.dockerRepository = dockerRepository;
    }

    private String id;
    private String lastVersion;
    private DockerRepository dockerRepository;

    @Override
    public String toString() {
        return new StringBuilder()
                .append(format("Docker_repo.host: %s", dockerRepository.getHost()))
                .append(format("Docker_repo.name: %s", dockerRepository.getName()))
                .append(format("Docker_repo.namespace: %s", dockerRepository.getPrefix()))
                .append(format("Id: %s\n", id))
                .append(format("Last Version: %s\n", lastVersion))
                .toString();
    }
}
