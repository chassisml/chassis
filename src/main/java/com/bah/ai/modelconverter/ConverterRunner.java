package com.bah.ai.modelconverter;

import com.amazonaws.services.ecr.AmazonECR;
import com.bah.ai.modelconverter.config.Configuration;
import com.bah.ai.modelconverter.dto.AssetVerifierDTO;
import com.bah.ai.modelconverter.validation.*;
import com.bah.ai.modelconverter.verification.*;
import lombok.extern.slf4j.Slf4j;
import org.yaml.snakeyaml.Yaml;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

@Slf4j
public class ConverterRunner {
    private static Configuration appConfig;
    private static ModelConverter converter;

    static {
        System.setProperty("org.apache.commons.logging.Log", "org.apache.commons.logging.impl.NoOpLog");
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: <file.yml>");
            return;
        }

        Yaml yaml = new Yaml();
        try (InputStream in = Files.newInputStream(Paths.get(args[0]))) {
            appConfig = yaml.loadAs(in, Configuration.class);
            log.info(appConfig.toString());
        } catch (IOException e) {
            log.error("It was not possible loading the application settings");
            return;
        }

        checkEnvVariables();

        String ecrURI = getECRUri(System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
        String ecrRepo = System.getenv(AppVariable.ECR_REPO.getAppVarName());
        converter = new ModelConverter(ecrURI, ecrRepo, appConfig);

        converter.setValidations(getAllValidations());
        converter.setVerifications(getAllVerifications());
        converter.validateAndVerify();

        String modelType = System.getenv(AppVariable.MODEL_TYPE.getAppVarName());
        AssetVerifierDTO paramsDTO = converter.getVerifications().get("PARAMS");
        ArchiveFileVerifier paramsVerifier = (ArchiveFileVerifier) paramsDTO.getVerifierObj();
        S3ArchiveHelper paramsHelper = paramsVerifier.getArchiveHelper();
        AssetVerifierDTO resourcesDTO = converter.getVerifications().get("RESOURCES");
        ArchiveFileVerifier resourcesVerifier = (ArchiveFileVerifier) resourcesDTO.getVerifierObj();
        AssetVerifierDTO modelTypeDTO = converter.getVerifications().get("ModelType");
        ModelTypeVerifier modelTypeVerifier = (ModelTypeVerifier) modelTypeDTO.getVerifierObj();
        byte[] modelArchiveContent = converter.processModelArchives(paramsHelper,
                paramsVerifier.getAsset(),
                resourcesVerifier.getAsset(),
                modelTypeVerifier.getAsset(),
                System.getenv(AppVariable.AWS_KEY_ID.getAppVarName()) +
                        System.getenv(AppVariable.AWS_SECRET_KEY.getAppVarName()) +
                        System.getenv(AppVariable.PLATFORM.getAppVarName()) +
                        System.getenv(AppVariable.MODEL_TYPE.getAppVarName()));

        if (modelArchiveContent != null) {
            AssetVerifierDTO ecrDTO = converter.getVerifications().get("ECR");
            boolean exportedToECR = converter.exportImageToECR((AmazonECR) ecrDTO.getVerifierObj().getAsset());
            if (exportedToECR) {
                AssetVerifierDTO importerDTO = converter.getVerifications().get("Importer");
                ImporterVerifier importerVerifier = (ImporterVerifier) importerDTO.getVerifierObj();
                String importerBaseURL = importerVerifier.getAsset();
                boolean successImporterCall = converter.callModelImporter(importerBaseURL, modelArchiveContent);
                if (successImporterCall) {
                    log.info("Model-converter workflow was successfully executed end-to-end!!");
                } else {
                    log.error("An error was detected while calling model importer");
                }
            } else {
                log.error("An error occurred while exporting the image to ECR...");
            }
        } else
            log.error("There was an error processing the model archive file");
    }

    public static Map<Validator, Map<AppVariable, String>> getAllValidations() {
        Map<Validator, Map<AppVariable, String>> validations = new LinkedHashMap<>();
        List<String> validationNames = Collections.unmodifiableList(new LinkedList<String>() {{
            add("AWS");
            add("ECR");
            add("ModelDir");
            add("ModelType");
            add("Importer");
        }});
        for (String validationName : validationNames) {
            Map.Entry<Validator, Map<AppVariable, String>> entryRef = createValidationEntry(validationName);
            validations.put(entryRef.getKey(), entryRef.getValue());
        }
        return validations;
    }

    private static Map<String, AssetVerifierDTO> getAllVerifications() {
        Map<String, AssetVerifierDTO> verifications = new LinkedHashMap<>();
        AssetVerifierDTO s3VerifierDTO = createVerifierDTO("S3");
        verifications.put("S3", s3VerifierDTO);

        AssetVerifierDTO paramsVerifierDTO = new AssetVerifierDTO();
        paramsVerifierDTO.setVerifierObj(new ArchiveFileVerifier("PARAMS", s3VerifierDTO.getVerifierObj(), converter.getTempSubdir()));
        paramsVerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("ASSET_DESC", "Parameters archive");
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), System.getenv(AppVariable.SAGEMAKER_BUCKET.getAppVarName()));
            put("ASSET_PATH", System.getenv(AppVariable.PARAMETERS_PATH.getAppVarName()));
        }});
        verifications.put("PARAMS", paramsVerifierDTO);

        AssetVerifierDTO resVerifierDTO = new AssetVerifierDTO();
        resVerifierDTO.setVerifierObj(new ArchiveFileVerifier("RESOURCES", s3VerifierDTO.getVerifierObj(), converter.getTempSubdir()));
        resVerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("ASSET_DESC", "Resources archive");
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), System.getenv(AppVariable.SAGEMAKER_BUCKET.getAppVarName()));
            put("ASSET_PATH", System.getenv(AppVariable.RESOURCES_PATH.getAppVarName()));
        }});
        verifications.put("RESOURCES", resVerifierDTO);

        AssetVerifierDTO ecrVerifierDTO = createVerifierDTO("ECR");
        verifications.put("ECR", ecrVerifierDTO);


        verifications.put("ModelDir", createVerifierDTO("ModelDir"));
        verifications.put("ModelType", createVerifierDTO("ModelType"));
        //verifications.put("Importer", createVerifierDTO("Importer"));

        return verifications;
    }

    private static Map.Entry<Validator, Map<AppVariable, String>> createValidationEntry(String validatorName) {
        Map.Entry<Validator, Map<AppVariable, String>> validatorEntry;
        Map<AppVariable, String> validatorConfig;
        Validator validatorObj;
        switch (validatorName) {
            case "AWS":
                validatorObj = new AWSValidator();
                validatorConfig = new HashMap<AppVariable, String>() {{
                    put(AppVariable.AWS_KEY_ID, System.getenv(AppVariable.AWS_KEY_ID.getAppVarName()));
                    put(AppVariable.AWS_SECRET_KEY, System.getenv(AppVariable.AWS_SECRET_KEY.getAppVarName()));
                }};
                break;
            case "ECR":
                validatorObj = new ECRValidator();
                validatorConfig = new HashMap<AppVariable, String>() {{
                    put(AppVariable.ECR_REGISTRY, System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
                    put(AppVariable.ECR_REPO, System.getenv(AppVariable.ECR_REPO.getAppVarName()));
                    put(AppVariable.ECR_USER, System.getenv(AppVariable.ECR_USER.getAppVarName()));
                }};
                break;
            case "ModelDir":
                validatorObj = new ModelDirValidator();
                validatorConfig = new HashMap<AppVariable, String>() {{
                    put(AppVariable.MODEL_DIR, appConfig.getResourceDir());
                }};
                break;
            case "ModelType":
                validatorObj = new ModelTypeValidator();
                validatorConfig = new HashMap<AppVariable, String>() {{
                    put(AppVariable.PLATFORM, System.getenv(AppVariable.PLATFORM.getAppVarName()));
                    put(AppVariable.MODEL_TYPE, System.getenv(AppVariable.MODEL_TYPE.getAppVarName()));
                }};
                break;
            case "Importer":
                validatorObj = new ImporterValidator();
                validatorConfig = new HashMap<AppVariable, String>() {{
                    put(AppVariable.IMPORTER_HOST, System.getenv(AppVariable.IMPORTER_HOST.getAppVarName()));
                    if (System.getenv().containsKey(AppVariable.IMPORTER_PORT.getAppVarName())) {
                        put(AppVariable.IMPORTER_PORT, System.getenv(AppVariable.IMPORTER_PORT.getAppVarName()));
                    }
                }};

                break;
            default:
                validatorObj = null;
                validatorConfig = null;
                break;
        }
        validatorEntry = new AbstractMap.SimpleEntry<>(validatorObj, validatorConfig);

        return validatorEntry;
    }

    public static AssetVerifierDTO createVerifierDTO(String verifierType) {
        AssetVerifierDTO assetVerifierObj = new AssetVerifierDTO();
        switch (verifierType) {
            case "ECR":
                assetVerifierObj.setVerifierObj(new ECRVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.ECR_REPO.getAppVarName(), System.getenv(AppVariable.ECR_REPO.getAppVarName()));
                }});
                break;
            case "ModelDir":
                assetVerifierObj.setVerifierObj(new ModelDirVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.MODEL_DIR.getAppVarName(), appConfig.getResourceDir());
                }});
                break;
            case "ModelType":
                assetVerifierObj.setVerifierObj(new ModelTypeVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.MODEL_DIR.getAppVarName(), appConfig.getResourceDir());
                    put(AppVariable.PLATFORM.getAppVarName(), System.getenv(AppVariable.PLATFORM.getAppVarName()));
                    put(AppVariable.MODEL_TYPE.getAppVarName(), System.getenv(AppVariable.MODEL_TYPE.getAppVarName()));
                }});
                break;
            case "Importer":
                assetVerifierObj.setVerifierObj(new ImporterVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.IMPORTER_HOST.getAppVarName(), System.getenv(AppVariable.IMPORTER_HOST.getAppVarName()));
                    if (System.getenv().containsKey(AppVariable.IMPORTER_PORT.getAppVarName())) {
                        put(AppVariable.IMPORTER_PORT.getAppVarName(), System.getenv(AppVariable.IMPORTER_PORT.getAppVarName()));
                    }
                }});
                break;
            case "S3":
                assetVerifierObj.setVerifierObj(new S3Verifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put("USER_ACCESS_KEY", System.getenv(AppVariable.AWS_KEY_ID.getAppVarName()));
                    put("USER_SECRET_KEY", System.getenv(AppVariable.AWS_SECRET_KEY.getAppVarName()));
                    put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), System.getenv(AppVariable.SAGEMAKER_BUCKET.getAppVarName()));
                }});
                break;
            default:
                assetVerifierObj = null;
                break;
        }

        return assetVerifierObj;
    }

    private static void checkEnvVariables() {
        boolean envVarsOk = true;
        for (AppVariable appVar : AppVariable.values()) {
            envVarsOk &= checkEnvVariable(appVar);
        }
        if (!envVarsOk) {
            throw new IllegalArgumentException("Missing some env variables");
        }
    }

    private static String getECRUri(String ecrRegistryURL) {
        return ecrRegistryURL.replace("https://", "");
    }

    private static boolean checkEnvVariable(AppVariable appVariable) {
        boolean isVarValid;
        String envVarName = appVariable.getAppVarName();
        String envValue = System.getenv(appVariable.getAppVarName());
        if (appVariable.isMandatory()) {
            if (envValue == null || "".equals(envValue.trim())) {
                log.warn(envVarName + ": not found");
                isVarValid = false;
            } else {
                log.info(envVarName + ": ok (length: " + envValue.length() + ")");
                isVarValid = true;
            }
        } else {
            log.info(envVarName + " is not mandatory ...");
            isVarValid = true;
        }

        return isVarValid;
    }

    public static void setAppConfig(Configuration appConfig) {
        ConverterRunner.appConfig = appConfig;
    }
}
