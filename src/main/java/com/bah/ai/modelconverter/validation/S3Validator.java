package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class S3Validator extends Validator {
    public S3Validator() {
        this.validatorType = "S3";
    }


    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (!parameters.containsKey(AppVariable.SAGEMAKER_BUCKET)) {
            this.message = "The user input S3 bucket is not properly set";
            throw new IllegalArgumentException(this.message);
        }

        if (!parameters.containsKey(AppVariable.RESOURCES_PATH)) {
            this.message = "The resources path value is not set as input variable";
            throw new IllegalArgumentException(this.message);
        }

        if (!parameters.containsKey(AppVariable.PARAMETERS_PATH)) {
            this.message = "The weights path value is not set as input variable";
            throw new IllegalArgumentException(this.message);
        }

        this.valid = true;
        this.message = "User has provided all required values for accessing resources and parameters";
        log.info(this.message);

        return this.valid;
    }
}
