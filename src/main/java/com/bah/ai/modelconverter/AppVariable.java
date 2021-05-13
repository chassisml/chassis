package com.bah.ai.modelconverter;

public enum AppVariable {
    AWS_KEY_ID("AWS_ACCESS_KEY_ID", true),
    AWS_SECRET_KEY("AWS_SECRET_ACCESS_KEY", true),
    ECR_REGISTRY("MODZY_MC_ECR_REGISTRY", true),
    ECR_REPO("MODZY_MC_ECR_REPO", true),
    ECR_USER("MODZY_MC_ECR_USER", true),
    MODEL_DIR("MODZY_MC_DIR", false),
    PARAMETERS_PATH("MODZY_MC_PARAMS_PATH", false),
    RESOURCES_PATH("MODZY_MC_RES_PATH", false),
    SAGEMAKER_BUCKET("MODZY_MC_SM_BUCKET", false),
    IMPORTER_HOST("MODZY_MI_HOST", true),
    IMPORTER_PORT("MODZY_MI_PORT", false),
    PLATFORM("MODZY_MC_PLATFORM", false),
    MODEL_TYPE("MODZY_MC_MODEL_TYPE", false),
    DOCKER_HOST("MODZY_MC_DOCKER_HOST", false),
    MODZY_ENVIRONMENT("MODZY_EXEC_ENVIRONMENT", true);

    protected String appVarName;
    protected boolean mandatory;

    AppVariable(String varName, boolean isMandatory) {
        this.appVarName = varName;
        this.mandatory = isMandatory;
    }

    public String getAppVarName() {
        return this.appVarName;
    }

    public boolean isMandatory() {
        return mandatory;
    }
}
