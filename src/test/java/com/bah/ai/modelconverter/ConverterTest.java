package com.bah.ai.modelconverter;

import com.amazonaws.services.ecr.AmazonECR;
import com.bah.ai.modelconverter.config.Configuration;
import com.bah.ai.modelconverter.dto.AssetVerifierDTO;
import com.bah.ai.modelconverter.verification.*;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.HttpStatusCode;
import org.yaml.snakeyaml.Yaml;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

import static com.github.stefanbirkner.systemlambda.SystemLambda.withEnvironmentVariable;
import static org.junit.jupiter.api.Assertions.*;

@Slf4j
public class ConverterTest {
    private static Configuration appConfig;
    private static ModelConverter converter;
    private static File converterDirectory;
    private static ClientAndServer mockServer = ClientAndServer.startClientAndServer(8080);

    public ConverterTest() {
        Yaml yaml = new Yaml();
        try (InputStream in = Files.newInputStream(Paths.get("src/main/resources/app_config.yml"))) {
            appConfig = yaml.loadAs(in, Configuration.class);
        } catch (IOException e) {
            log.error("There was an error reading the application configuration file.", e);
        }
    }

    @Test
    public void setEnvironmentVariable() throws Exception {
        List<String> values = withEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .and("MODZY_MC_ECR_REGISTRY", "https://326081595054.dkr.ecr.us-east-1.amazonaws.com")
                .and("MODZY_MC_ECR_REPO", "sagemaker-testing")
                .and("MODZY_MC_ECR_USER", "AWS")
                .and("MODZY_MC_RES_PATH", "yolo/resources.tar.gz")
                .and("MODZY_MC_PARAMS_PATH", "yolo/weights.tar.gz")
                .and("MODZY_MC_MODEL_TYPE", "yolo")
                .and("MODZY_MC_SM_BUCKET", "sagemaker-testing-ds")
                .and("MODZY_MI_HOST", "localhost")
                .execute(() -> Arrays.asList(
                        System.getenv("AWS_ACCESS_KEY_ID"),
                        System.getenv("AWS_SECRET_ACCESS_KEY"),
                        System.getenv("MODZY_MC_ECR_REGISTRY"),
                        System.getenv("MODZY_MC_ECR_REPO"),
                        System.getenv("MODZY_MC_ECR_USER"),
                        System.getenv("MODZY_MC_RES_PATH"),
                        System.getenv("MODZY_MC_PARAMS_PATH"),
                        System.getenv("MODZY_MC_MODEL_TYPE"),
                        System.getenv("MODZY_MC_SM_BUCKET"),
                        System.getenv("MODZY_MI_HOST")
                ));
        assertEquals(
                Arrays.asList("AKIAUX272I2XL6D3MX7N",
                        "M3Yq1VGhOaySVp8YjXRCZcOXl5zj5kNvgOVk5Oh4",
                        "https://326081595054.dkr.ecr.us-east-1.amazonaws.com",
                        "sagemaker-testing",
                        "AWS",
                        "yolo/resources.tar.gz",
                        "yolo/weights.tar.gz",
                        "yolo",
                        "sagemaker-testing-ds",
                        "localhost"),
                values
        );
    }

    @Test
    public void testModelDirProcessing() throws Exception {
        withEnvironmentVariable("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .and("MODZY_MC_ECR_REGISTRY", "https://326081595054.dkr.ecr.us-east-1.amazonaws.com")
                .and("MODZY_MC_ECR_REPO", "sagemaker-testing")
                .and("MODZY_MC_RES_PATH", "yolo/resources.tar.gz")
                .and("MODZY_MC_PARAMS_PATH", "yolo/weights.tar.gz")
                .and("MODZY_MC_MODEL_TYPE", "yolo")
                .and("MODZY_MC_SM_BUCKET", "sagemaker-testing-ds")
                .execute(() -> {
                    String ecrURI = getECRUri(System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
                    String ecrRepo = System.getenv(AppVariable.ECR_REPO.getAppVarName());
                    converter = new ModelConverter(ecrURI, ecrRepo, appConfig);

                    converter.setVerifications(getModelDirVerifications());
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
                    converterDirectory = paramsVerifier.getAsset().getParentFile();
                });
        assertTrue(new LinkedList<String>() {{
            add("archives");
            add("assets");
            add("model_dir");
        }}.containsAll(Arrays.asList(converterDirectory.getParentFile().list())));
    }

    @Test
    public void testModelImporterCall() throws Exception {
        mockServer.when(new HttpRequest().withMethod("GET").withPath("/status"))
                .respond(new HttpResponse().withStatusCode(HttpStatusCode.OK_200.code())
                        .withBody("Importer server working ")
                );

        mockServer.when(new HttpRequest().withMethod("POST").withPath("/import"))
                .respond(new HttpResponse().withStatusCode(HttpStatusCode.OK_200.code())
                        .withBody("Models imported: 0")
                );

        withEnvironmentVariable("MODZY_MI_HOST", "localhost")
                .and("MODZY_MI_PORT", "8080")
                .and("MODZY_MC_ECR_REGISTRY", "https://326081595054.dkr.ecr.us-east-1.amazonaws.com")
                .and("MODZY_MC_ECR_REPO", "sagemaker-testing")
                .and("MODZY_MC_RES_PATH", "yolo/resources.tar.gz")
                .and("MODZY_MC_PARAMS_PATH", "yolo/weights.tar.gz")
                .and("MODZY_MC_MODEL_TYPE", "yolo")
                .and("MODZY_MC_SM_BUCKET", "sagemaker-testing-ds")
                .and("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .execute(() -> {
                    String ecrURI = getECRUri(System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
                    String ecrRepo = System.getenv(AppVariable.ECR_REPO.getAppVarName());
                    converter = new ModelConverter(ecrURI, ecrRepo, appConfig);

                    converter.setVerifications(getModelDirVerifications());
                    converter.getVerifications().put("Importer", createVerifierDTO("Importer"));
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

                    AssetVerifierDTO importerDTO = converter.getVerifications().get("Importer");
                    ImporterVerifier importerVerifier = (ImporterVerifier) importerDTO.getVerifierObj();
                    String importerBaseURL = importerVerifier.getAsset();
                    boolean successImporterCall = converter.callModelImporter(importerBaseURL, modelArchiveContent);
                    assertFalse(successImporterCall);
                });
    }

    @Test
    public void testPublishingDockerImage() throws Exception {
        withEnvironmentVariable("MODZY_MC_ECR_REGISTRY", "https://326081595054.dkr.ecr.us-east-1.amazonaws.com")
                .and("MODZY_MC_ECR_REPO", "sagemaker-testing")
                .and("AWS_ACCESS_KEY_ID", "AKIAUX272I2XL6D3MX7N")
                .and("AWS_SECRET_ACCESS_KEY", "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")
                .and("MODZY_MC_DOCKER_HOST", "unix:///var/run/docker.sock")
                // TODO: Get this running within the CircleCI instance
                // .and("MODZY_MC_DOCKER_HOST", "tcp://10.6.2.84:2376")
                .execute(() -> {
                    String ecrURI = getECRUri(System.getenv(AppVariable.ECR_REGISTRY.getAppVarName()));
                    String ecrRepo = System.getenv(AppVariable.ECR_REPO.getAppVarName());
                    converter = new ModelConverter(ecrURI, ecrRepo, appConfig);
                    converter.validateAndVerify();

                    converter.setTempModelDir(new File("src/resources/yolo"));

                    String converterFileName = converter.getTempModelDir().getParentFile().getName();
                    String hashedModelDir = converterFileName.substring(9);
                    converter.setImageName("converted-model-" + hashedModelDir);

                    AssetVerifierDTO dockerDTO = converter.getVerifications().get("DOCKER");
                    AssetVerifierDTO ecrDTO = converter.getVerifications().get("ECR");
                    boolean exportedToECR = converter.exportImageToECR((AmazonECR) ecrDTO.getVerifierObj().getAsset());
                    assertTrue(exportedToECR);
                });
    }

    private static Map<String, AssetVerifierDTO> getModelDirVerifications() {
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

        return verifications;
    }

    private static AssetVerifierDTO createVerifierDTO(String verifierType) {
        AssetVerifierDTO assetVerifierObj = new AssetVerifierDTO();
        switch (verifierType) {
            case "ECR":
                assetVerifierObj.setVerifierObj(new ECRVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.ECR_REPO.getAppVarName(), System.getenv(AppVariable.ECR_REPO.getAppVarName()));
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
            case "Importer":
                assetVerifierObj.setVerifierObj(new ImporterVerifier());
                assetVerifierObj.setVerifierSettings(new HashMap<String, String>() {{
                    put(AppVariable.IMPORTER_HOST.getAppVarName(), System.getenv(AppVariable.IMPORTER_HOST.getAppVarName()));
                    put(AppVariable.IMPORTER_PORT.getAppVarName(), System.getenv(AppVariable.IMPORTER_PORT.getAppVarName()));
                }});
                break;
            default:
                assetVerifierObj = null;
                break;
        }

        return assetVerifierObj;
    }

    private static String getECRUri(String ecrRegistryURL) {
        return ecrRegistryURL.replace("https://", "");
    }
}
