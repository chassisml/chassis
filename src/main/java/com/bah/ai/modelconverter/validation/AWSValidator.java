package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class AWSValidator extends Validator {
    public AWSValidator() {
        this.validatorType = "AWS";
    }

    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (parameters.containsKey(AppVariable.AWS_KEY_ID) && parameters.containsKey(AppVariable.AWS_SECRET_KEY)) {
            this.message = "There were found AWS access keys and set properly";
            this.valid = true;
            log.info(this.message);
        } else {
            this.message = "User did not provide AWS Credentials";
            throw new IllegalArgumentException(this.message);
        }

        return this.valid;
    }
}
