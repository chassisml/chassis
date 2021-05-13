package com.bah.ai.modelconverter.api.service;

import com.amazonaws.services.ecr.AmazonECR;
import com.bah.ai.modelconverter.AppVariable;
import com.bah.ai.modelconverter.ConverterRunner;
import com.bah.ai.modelconverter.ModelConverter;
import com.bah.ai.modelconverter.S3ArchiveHelper;
import com.bah.ai.modelconverter.api.dto.OperationResponseDTO;
import com.bah.ai.modelconverter.config.Configuration;
import com.bah.ai.modelconverter.dto.AssetVerifierDTO;
import com.bah.ai.modelconverter.validation.*;
import com.bah.ai.modelconverter.verification.*;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.yaml.snakeyaml.Yaml;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

@Slf4j
@Getter
@Service
public class ModelConverterService {
    private Configuration appConfig;

    private final String ecrRegistry = System.getenv(AppVariable.ECR_REGISTRY.getAppVarName());
    private final String ecrRepo = System.getenv(AppVariable.ECR_REPO.getAppVarName());
    private final String appConfigFile = System.getenv(AppVariable.MODEL_DIR.getAppVarName());
    private final String modzyEnv = System.getenv(AppVariable.MODZY_ENVIRONMENT.getAppVarName());
    private final String ecrURI;

    public ModelConverterService(){
        Yaml yaml = new Yaml();
        try (InputStream in = Files.newInputStream(Paths.get(appConfigFile))) {
            appConfig = yaml.loadAs(in, Configuration.class);
            log.info(appConfig.toString());
        } catch (IOException e) {
            log.error("It was not possible loading the application settings");
        }
        ecrURI = ecrRegistry.replace("https://", "");
        ConverterRunner.setAppConfig(appConfig);
    }

    public OperationResponseDTO checkEnvironment(){
        OperationResponseDTO response = new OperationResponseDTO();
        boolean envVarsOk = true;
        int missingEnVars = 0;
        for (AppVariable appVar : AppVariable.values()) {
            boolean envVarOk = checkEnvVariable(appVar);
            missingEnVars += (envVarOk) ? 0 : 1;
            envVarsOk &= envVarOk;
        }
        if (envVarsOk) {
            OperationResponseDTO.ResponseEntry okResponse = new OperationResponseDTO.ResponseEntry();
            okResponse.setHttpCode("200");
            okResponse.setMessage("All the required environment variables are set!!");
            response.getResponseEntries().add(okResponse);
        }
        else {
            OperationResponseDTO.ResponseEntry missingResponse = new OperationResponseDTO.ResponseEntry();
            missingResponse.setHttpCode("500");
            missingResponse.setMessage("There are " + missingEnVars + " environment variables missing");
            response.getResponseEntries().add(missingResponse);
        }

        return response;
    }

    public OperationResponseDTO checkIntegrations(String key_id,
                                                  String access_key,
                                                  String s3Bucket,
                                                  String paramsPath,
                                                  String resourcesPath,
                                                  String platform,
                                                  String model_type){
        ModelConverter converter = new ModelConverter(ecrURI, ecrRepo, appConfig);
        converter.setValidations(getAllValidations(converter, key_id, access_key, s3Bucket, paramsPath, resourcesPath, platform, model_type));
        converter.setVerifications(getAllVerification(converter, key_id, access_key, s3Bucket, paramsPath, resourcesPath, platform, model_type));
        converter.validateAndVerify();

        OperationResponseDTO response = new OperationResponseDTO();
        for(Map.Entry<String, String> clientError : converter.getClientErrors().entrySet()){
            OperationResponseDTO.ResponseEntry responseEntry = new OperationResponseDTO.ResponseEntry();
            responseEntry.setHttpCode(clientError.getKey());
            responseEntry.setMessage(clientError.getValue());
            response.getResponseEntries().add(responseEntry);
        }
        if (converter.getClientErrors().isEmpty()) {
            OperationResponseDTO.ResponseEntry okResponse = new OperationResponseDTO.ResponseEntry();
            okResponse.setHttpCode("200");
            okResponse.setMessage("All the validations and verifications seem to be working correctly!");
            response.getResponseEntries().add(okResponse);
        }

        return response;
    }

    public OperationResponseDTO executeConverter(String key_id,
                                                 String access_key,
                                                 String s3Bucket,
                                                 String paramsPath,
                                                 String resourcesPath,
                                                 String platform,
                                                 String model_type){
        ModelConverter converter = new ModelConverter(ecrURI, ecrRepo, appConfig);
        converter.setValidations(ConverterRunner.getAllValidations());
        converter.setVerifications(getAllVerification(converter, key_id, access_key, s3Bucket, paramsPath, resourcesPath, platform, model_type));
        converter.validateAndVerify();

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
                key_id + access_key + platform + model_type);

        OperationResponseDTO response = new OperationResponseDTO();
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

                    OperationResponseDTO.ResponseEntry okResponse = new OperationResponseDTO.ResponseEntry();
                    okResponse.setHttpCode("200");
                    okResponse.setMessage("Model converter finished the execution of the integration endpoints!");
                    response.getResponseEntries().add(okResponse);

                    OperationResponseDTO.SuccessEntry successData = new OperationResponseDTO.SuccessEntry();
                    successData.setModelId(converter.getModelId());
                    successData.setModelName(converter.getImageName());
                    successData.setEcrURL(converter.getEcrURL());
                    successData.setModelVersion(converter.getModelVersion());
                    String modelURL = "https://" + modzyEnv + "/models/" + converter.getModelId() + "-modzy-" + model_type + "/" + converter.getModelVersion();
                    successData.setModelURL(modelURL);
                    response.setSuccessEntry(successData);
                } else {
                    log.error("An error was detected while calling model importer");
                }
            } else {
                log.error("An error occurred while exporting the image to ECR...");
            }
        } else
            log.error("There was an error processing the model archive file");

        for(Map.Entry<String, String> clientError : converter.getClientErrors().entrySet()){
            OperationResponseDTO.ResponseEntry responseEntry = new OperationResponseDTO.ResponseEntry();
            responseEntry.setHttpCode(clientError.getKey());
            responseEntry.setMessage(clientError.getValue());
            response.getResponseEntries().add(responseEntry);
        }

        return response;
    }

    private static Map<String, AssetVerifierDTO> getAllVerification(ModelConverter converter,
                                                                    String key_id,
                                                                    String access_key,
                                                                    String s3Bucket,
                                                                    String paramsPath,
                                                                    String resourcesPath,
                                                                    String platform,
                                                                    String model_type){
        Map<String, AssetVerifierDTO> verifications = new LinkedHashMap<>();
        AssetVerifierDTO s3VerifierDTO = new AssetVerifierDTO();
        s3VerifierDTO.setVerifierObj(new S3Verifier());
        s3VerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("USER_ACCESS_KEY", key_id);
            put("USER_SECRET_KEY", access_key);
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), s3Bucket);
        }});
        verifications.put("S3", s3VerifierDTO);

        AssetVerifierDTO paramsVerifierDTO = new AssetVerifierDTO();
        paramsVerifierDTO.setVerifierObj(new ArchiveFileVerifier("PARAMS", s3VerifierDTO.getVerifierObj(), converter.getTempSubdir()));
        paramsVerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("ASSET_DESC", "Parameters archive");
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), s3Bucket);
            put("ASSET_PATH", paramsPath);
        }});
        verifications.put("PARAMS", paramsVerifierDTO);

        AssetVerifierDTO resVerifierDTO = new AssetVerifierDTO();
        resVerifierDTO.setVerifierObj(new ArchiveFileVerifier("RESOURCES", s3VerifierDTO.getVerifierObj(), converter.getTempSubdir()));
        resVerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put("ASSET_DESC", "Resources archive");
            put(AppVariable.SAGEMAKER_BUCKET.getAppVarName(), s3Bucket);
            put("ASSET_PATH", resourcesPath);
        }});
        verifications.put("RESOURCES", resVerifierDTO);

        AssetVerifierDTO ecrVerifierDTO = ConverterRunner.createVerifierDTO("ECR");
        verifications.put("ECR", ecrVerifierDTO);

        AssetVerifierDTO modelTypeVerifierDTO = new AssetVerifierDTO();
        modelTypeVerifierDTO.setVerifierObj(new ModelTypeVerifier());
        modelTypeVerifierDTO.setVerifierSettings(new HashMap<String, String>() {{
            put(AppVariable.MODEL_DIR.getAppVarName(), converter.getAppConfigValues().getResourceDir());
            put(AppVariable.PLATFORM.getAppVarName(), platform);
            put(AppVariable.MODEL_TYPE.getAppVarName(), model_type);
        }});
        verifications.put("ModelType", modelTypeVerifierDTO);

        verifications.put("ModelDir", ConverterRunner.createVerifierDTO("ModelDir"));
        verifications.put("Importer", ConverterRunner.createVerifierDTO("Importer")); // Toggle to turn importer

        return verifications;
    }

    public static Map<Validator, Map<AppVariable, String>> getAllValidations(ModelConverter converter,
                                                                             String key_id,
                                                                             String access_key,
                                                                             String s3Bucket,
                                                                             String paramsPath,
                                                                             String resourcesPath,
                                                                             String platform,
                                                                             String model_type) {
        Map<Validator, Map<AppVariable, String>> validations = new LinkedHashMap<>();
        List<String> validationNames = Collections.unmodifiableList(new LinkedList<String>() {{
            add("AWS");
            add("S3");
            add("ModelDir");
            add("ModelType");
            add("Importer");
        }});
        for (String validationName : validationNames) {
            Map.Entry<Validator, Map<AppVariable, String>> validatorEntry;
            Map<AppVariable, String> validatorConfig;
            Validator validatorObj;
            switch (validationName) {
                case "AWS":
                    validatorObj = new AWSValidator();
                    validatorConfig = new HashMap<AppVariable, String>() {{
                        put(AppVariable.AWS_KEY_ID, key_id);
                        put(AppVariable.AWS_SECRET_KEY, access_key);
                    }};
                    break;
                case "S3":
                    validatorObj = new S3Validator();
                    validatorConfig = new HashMap<AppVariable, String>() {{
                        put(AppVariable.SAGEMAKER_BUCKET, s3Bucket);
                        put(AppVariable.RESOURCES_PATH, paramsPath);
                        put(AppVariable.PARAMETERS_PATH, resourcesPath);
                    }};
                    break;
                case "ECR":
                    validatorObj = new S3Validator();
                    validatorConfig = new HashMap<AppVariable, String>() {{
                        put(AppVariable.ECR_REGISTRY, System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
                        put(AppVariable.ECR_REPO, System.getenv(AppVariable.ECR_REPO.getAppVarName()));
                        put(AppVariable.ECR_USER, System.getenv(AppVariable.ECR_USER.getAppVarName()));
                    }};
                    break;
                case "ModelDir":
                    validatorObj = new ModelDirValidator();
                    validatorConfig = new HashMap<AppVariable, String>() {{
                        put(AppVariable.MODEL_DIR, converter.getAppConfigValues().getResourceDir());
                    }};
                    break;
                case "ModelType":
                    validatorObj = new ModelTypeValidator();
                    validatorConfig = new HashMap<AppVariable, String>() {{
                        put(AppVariable.PLATFORM, platform);
                        put(AppVariable.MODEL_TYPE, model_type);
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
            validations.put(validatorEntry.getKey(), validatorEntry.getValue());
        }
        return validations;
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
}
