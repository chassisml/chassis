package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.io.IOException;
import java.nio.file.NotDirectoryException;
import java.util.Map;

@Slf4j
public class ModelDirValidator extends Validator {
    public ModelDirValidator() {
        this.validatorType = "ModelDir";
    }

    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (parameters.containsKey(AppVariable.MODEL_DIR)) {
            this.valid = true;
            this.message = "Model directory is properly set";
            log.info(this.message);
        } else {
            this.message = "The model converter directory app variable is not set";
            throw new IllegalArgumentException(this.message);
        }
        return this.valid;
    }
}
