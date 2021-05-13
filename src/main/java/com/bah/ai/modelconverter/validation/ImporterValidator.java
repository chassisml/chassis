package com.bah.ai.modelconverter.validation;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class ImporterValidator extends Validator {
    public ImporterValidator() {
        this.validatorType = "Importer";
    }

    @Override
    public boolean validate(Map<AppVariable, String> parameters) {
        if (parameters.containsKey(AppVariable.IMPORTER_HOST)) {
            this.message = "Importer host is set appropriately";
            this.valid = true;
            log.info(this.message);
        } else {
            this.message = "Model importer is missing its host setting";
            throw new IllegalArgumentException(this.message);
        }

        return this.valid;
    }
}
