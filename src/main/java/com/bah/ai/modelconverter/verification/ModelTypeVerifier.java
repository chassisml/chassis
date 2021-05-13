package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

@Slf4j
public class ModelTypeVerifier extends AssetVerifier<File> {
    public ModelTypeVerifier() {
        this.assetName = "ModelType";
    }

    @Override
    public boolean verify(Map<String, String> parameters) {
        boolean verified = false;
        try {
            String resourcesDir = parameters.get(AppVariable.MODEL_DIR.getAppVarName());
            String platform = parameters.get(AppVariable.PLATFORM.getAppVarName());
            String modelType = parameters.get(AppVariable.MODEL_TYPE.getAppVarName());
            Path modelTypePath = Paths.get(resourcesDir, platform, modelType);
            this.asset = modelTypePath.toFile();
            if (asset.exists() && asset.isDirectory()) {
                verified = true;
                log.info("Access to a supported model directory is confirmed.");
            } else {
                this.failureReason = String.format("Platform '{}' and model type '{}' is not supported on this model converter", platform, modelType);
                log.error(this.failureReason);
            }
        } catch (Exception e) {
            this.failureReason = "A general error was raised when verifying the model type in catalog";
            log.error(this.failureReason, e);
        }
        return verified;
    }
}
