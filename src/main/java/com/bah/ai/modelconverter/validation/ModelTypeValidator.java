package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class ModelTypeValidator extends Validator {
    public ModelTypeValidator() {
        this.validatorType = "ModelType";
    }

    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (parameters.containsKey(AppVariable.PLATFORM) && parameters.containsKey(AppVariable.MODEL_TYPE)) {
            this.message = "Platform and model type is set properly";
            this.valid = true;
            log.info(this.message);
        } else {
            this.message = "User did not provide the platform and model type parameters";
            throw new IllegalArgumentException(this.message);
        }

        return this.valid;
    }
}
