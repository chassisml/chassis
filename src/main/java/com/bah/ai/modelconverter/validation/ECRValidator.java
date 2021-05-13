package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.util.Map;

@Slf4j
public class ECRValidator extends Validator {
    public ECRValidator() {
        this.validatorType = "ECR";
    }

    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (!parameters.containsKey(AppVariable.ECR_REGISTRY)) {
            this.message = "The ECR registry URL is not properly set";
            throw new IllegalArgumentException(this.message);
        }

        if (!parameters.containsKey(AppVariable.ECR_REPO)) {
            this.message = "The ECR repository value is not set as environment variable";
            throw new IllegalArgumentException(this.message);
        }

        if (!parameters.containsKey(AppVariable.ECR_USER)) {
            this.message = "The user for connectivity to ECR is not set";
            throw new IllegalArgumentException(this.message);
        }

        this.valid = true;
        this.message = "User has provided all required ECR environment variables";
        log.info(this.message);

        return this.valid;
    }
}
