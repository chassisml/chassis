package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;

import java.io.IOException;
import java.util.Map;
import java.util.Objects;

public abstract class Validator {
    protected String validatorType;
    protected String message = "";
    protected boolean valid = false;

    public String getMessage() {
        return message;
    }

    public boolean isValid() {
        return valid;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Validator validator = (Validator) o;
        return validatorType.equals(validator.validatorType);
    }

    @Override
    public int hashCode() {
        return Objects.hash(validatorType);
    }

    public abstract boolean validate(Map<AppVariable, String> parameters);
}
