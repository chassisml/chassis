package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.nio.file.NotDirectoryException;
import java.util.Map;

@Slf4j
public class ModelDirVerifier extends AssetVerifier<File> {
    public ModelDirVerifier() {
        this.assetName = "ModelDir";
    }

    @Override
    public boolean verify(Map<String, String> parameters) {
        boolean verified = false;
        try {
            String dirName = parameters.get(AppVariable.MODEL_DIR.getAppVarName());
            this.asset = new File(dirName);
            if (asset.exists() && asset.isDirectory()) {
                verified = true;
                log.info("Access to the model directory is confirmed.");
            } else {
                this.failureReason = "The directory '" + dirName + "' for model converter does not exist or is not accessible";
                log.error(this.failureReason);
            }
        } catch (Exception e) {
            this.failureReason = "There was a general error while verifying the model resources directory";
            log.error(this.failureReason, e);
        }

        return verified;
    }
}
