package com.bah.ai.modelconverter;

import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.model.*;
import com.bah.ai.modelconverter.config.AssetConfig;
import com.bah.ai.modelconverter.config.Configuration;
import com.bah.ai.modelconverter.config.DockerRepository;
import com.bah.ai.modelconverter.dto.AssetVerifierDTO;
import com.bah.ai.modelconverter.validation.Validator;
import com.bah.ai.modelconverter.verification.AssetVerifier;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ByteArrayEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.rauschig.jarchivelib.ArchiveFormat;
import org.rauschig.jarchivelib.Archiver;
import org.rauschig.jarchivelib.ArchiverFactory;
import org.rauschig.jarchivelib.CompressionType;
import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.nodes.Tag;

import javax.validation.ValidationException;
import java.io.*;
import java.net.MalformedURLException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Slf4j
public class ModelConverter {
    private Map<Validator, Map<AppVariable, String>> validations;

    private Map<String, AssetVerifierDTO> verifications;

    private String ecrURI;
    private String ecrRepo;
    private String modelId;
    private String imageName;
    private String ecrURL;
    private String modelVersion;
    private String modelName;
    private String hashBase;

    private File tempModelDir;
    private File tmpSubDir;

    private Configuration appConfigValues;

    private Map<String, String> clientErrors;

    public ModelConverter(String ecrURI, String ecrRepo, Configuration appConfig){
        this.ecrURI = ecrURI;
        this.ecrRepo = ecrRepo;
        this.appConfigValues = appConfig;
        this.clientErrors = new LinkedHashMap<>();

        try {
            Path workingDirPath = Paths.get(appConfigValues.getWorkingDir());
            workingDirPath.toFile().mkdirs();
            tmpSubDir = Files.createTempDirectory(workingDirPath, "converter").toFile();
            tmpSubDir.mkdirs();
        } catch (IOException e) {
            log.error("There was a problem creating a temporary directory for this converter execution", e);
        }
    }

    public void validateAndVerify(){
        StringBuilder invalidMessage = new StringBuilder("Validation errors for converter: ");
        if (validations != null){
            boolean validSettings = true;
            for(Validator validator: validations.keySet()){
                Map<AppVariable, String> params = validations.get(validator);
                validSettings &= validator.validate(params);
                if (!validator.isValid()){
                    invalidMessage.append("\n    ");
                    invalidMessage.append( validator.getMessage() );
                }
            }
            if (validSettings){
                log.info("Validation rules passed successfully");
            }
            else{
                clientErrors.put("400", invalidMessage.toString());
                log.error("There are some validation errors, check the stack trace");
                throw new ValidationException(invalidMessage.toString());
            }
        }
        else{
            log.info("There are not validations set up for check");
        }

        StringBuilder failureMessage = new StringBuilder("Verification errors for converter: ");
        if (verifications != null){
            boolean assetsVerified = true;
            for(String verifierKey: verifications.keySet()){
                AssetVerifierDTO verifierDTO = verifications.get(verifierKey);
                AssetVerifier verifier = verifierDTO.getVerifierObj();
                Map<String, String> params = verifierDTO.getVerifierSettings();
                assetsVerified &= verifier.verify(params);
                if (verifier.getFailureReason()!=null && !verifier.getFailureReason().isEmpty()){
                    failureMessage.append("\n    ");
                    failureMessage.append( verifier.getFailureReason() );
                }
            }
            if (assetsVerified){
                log.info("Asset verifications passed successfully");
            }
            else{
                clientErrors.put("403", failureMessage.toString());
                log.error("There are some verification errors, check the stack trace");
                throw new ValidationException(failureMessage.toString());
            }
        }
        else{
            log.info("There are not asset verifications set up for check");
        }
    }

    public byte[] processModelArchives(S3ArchiveHelper helper, File wArchiveDir, File rArchiveDir, File modelType, String userSelection){
        byte[] assetBundleContent = null;
        try {
            hashBase = userSelection;
            tempModelDir = copyModelLibrary(modelType);

            File tempAssetDir = copyAssetBundleDir(modelType);

            Path tempModelFileLocation = Paths.get(rArchiveDir.toString(), appConfigValues.getModelFileName());
            retrieveModelInfo(tempModelFileLocation.toFile());

            copyModelFile(rArchiveDir, tempAssetDir);
            copyModelArtifacts(wArchiveDir, tempModelDir, appConfigValues.getParamsDirName());
            copyModelArtifacts(rArchiveDir, tempModelDir, appConfigValues.getOtherResDirName());

            createConfigFile(tempAssetDir);

            assetBundleContent = getBinaryAssetBundle(helper, tempAssetDir);
            log.info("Model directory was correctly created at the following location {}", helper.getAssetDir());
        } catch (IOException ioex) {
            String msg = "There was an error while processing the model archive and directories: " + ioex.getMessage();
            clientErrors.put("503", msg);
            log.error(msg, ioex);
        }

        return assetBundleContent;
    }

    public boolean exportImageToECR(AmazonECR ecrClient) {
        boolean exported = false;

        String newRepoName = String.format("%s/%s", ecrRepo, imageName);
        try {
            CreateRepositoryRequest createRepoRequest = new CreateRepositoryRequest().withRepositoryName(newRepoName);
            CreateRepositoryResult createRepoResponse = ecrClient.createRepository(createRepoRequest);
        }
        catch (RepositoryAlreadyExistsException existingRepoException){
            log.info("The repo '" + newRepoName +"' already exists in the registry, " + ecrURI);
        }
        catch (Exception ex){
            String msg = "There was a problem while creating a new  repo" + newRepoName;
            clientErrors.put("400", msg);
            log.error(msg, ex);
            return false;
        }

        Archiver modelDirArchiver = ArchiverFactory.createArchiver(ArchiveFormat.TAR, CompressionType.GZIP);
        try {
            modelDirArchiver.create("context.tar.gz", tmpSubDir, tempModelDir);
        } catch (IOException ioex) {
            String msg = "There was a problem archiving the model container context into " + tempModelDir;
            clientErrors.put("400", msg);
            log.error(msg, ioex);
            return false;
        }

        Runtime runtime = Runtime.getRuntime();
        Process process;

        log.info("Caching the root file system.");
        try {
            runtime.exec("/kaniko/model-converter/snapshot.sh");
        } catch (IOException e) {
            e.printStackTrace();
        }
        log.info("Completed Caching the root file system.");

        try{
            String kanikoContext = "tar://" + new File(tmpSubDir, "context.tar.gz").getAbsolutePath();
            String destination = String.format("%s/%s:%s", ecrURI, newRepoName, modelVersion);
            log.info("Beginning to push image: " + imageName + " into registry " + ecrURI);
            String command = String.format("kaniko --context %s --destination %s", kanikoContext, destination);
            log.info("Executing: \"" + command + "\"");
            process = runtime.exec(command);

            long startTime = System.nanoTime();
            int totalWaitTIme = 0;
            int timeoutMin = appConfigValues.getKanikoTimeout();
            int kanikoWaitTime = appConfigValues.getKanikoWaitTime();
            while(!process.waitFor(kanikoWaitTime, TimeUnit.MINUTES)){
                totalWaitTIme += kanikoWaitTime;
                if (totalWaitTIme < timeoutMin) {
                    log.info("Kaniko is building and pushing your image, elapsed time {} minutes", totalWaitTIme);
                    BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    for(String s; (s = stdInput.readLine()) != null; ) log.info("KANIKO: {} ", s);
                }
                else {
                    log.error("Total elapsed time is greater than allowed time to build the image {}", timeoutMin);
                    exported = false;
                    break;
                }
            }
            long endTime = System.nanoTime();
            log.info("Kaniko executed in {} milliseconds", (endTime - startTime)/1000000);

            if (process.exitValue() != 0){
                log.error("There was an error risen while executing kaniko");
                exported = false;
            }
            else{
                String registryId = ecrURI.substring(0, ecrURI.indexOf(".dkr"));
                ListImagesRequest request = new ListImagesRequest()
                        .withRegistryId(registryId)
                        .withRepositoryName(newRepoName)
                        .withFilter(new ListImagesFilter().withTagStatus(TagStatus.TAGGED));
                ListImagesResult response = ecrClient.listImages(request);
                for(ImageIdentifier imgIds: response.getImageIds()){
                    if (imgIds.getImageTag().equals(modelVersion)){
                        log.info("Image pushed to repository " + newRepoName);
                        String fullECRRepo = "/v2/" + newRepoName + "/manifests/";
                        ecrURL = "https://" + ecrURI + fullECRRepo + modelVersion;
                        log.info("Push completed, you can find your image at: " + ecrURL);
                        exported = true;
                        break;
                    }
                }
            }
        } catch (Exception ioe) {
            String msg = "Error executing kaniko command";
            clientErrors.put("500", msg);
            log.error(msg, ioe);
            exported = false;
        }

        log.info("Resetting the root file system.");
        String[] dirs = {"bin","boot","dev","etc","home","lib","lib64","local","media","mnt","opt","root","run","sbin","srv","tmp","usr","var","workspace"};
        for (String dir : dirs) {
            runtime = Runtime.getRuntime();
            String cpCommand = String.format("/kaniko/bin/cp -r /kaniko/%s /", dir);
            try {
                process = runtime.exec(cpCommand);
                BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));
                for(String s; (s = stdInput.readLine()) != null; ) log.info("RESET KANIKO: {} ", s);
            }
            catch (Exception ex) {
                String msg = String.format("There was an issue when copying the directory '%s' to root", dir);
                clientErrors.put("500", msg);
                log.error(msg, ex);
                exported = false;
                break;
            }
        }
        log.info("Completed resetting the root file system.");

        return exported;
    }

    public boolean callModelImporter(String baseURL, byte[] postData){
        boolean successImport = false;
        String importModelURLStr = baseURL + "import?m=" + modelId + "&skip-containers=false";
        log.info("Calling model importer with URL: " + importModelURLStr);
        try {
            CloseableHttpClient client = HttpClients.createDefault();
            HttpPost httpPost = new HttpPost(importModelURLStr);
            httpPost.addHeader("User-Agent", "Java client");
            httpPost.addHeader("Content-Type", "application/gzip");
            ByteArrayEntity entity = new ByteArrayEntity(postData);
            httpPost.setEntity(entity);

            CloseableHttpResponse response = client.execute(httpPost);
            StringBuilder content;
            try (BufferedReader br = new BufferedReader(new InputStreamReader(response.getEntity().getContent()))) {
                String line;
                content = new StringBuilder();
                while ((line = br.readLine()) != null) {
                    content.append(line);
                    content.append(System.lineSeparator());
                }
            }

            String importerResponse = content.toString();
            if (importerResponse.contains("Models imported: 0")){
                String msg = "There was a problem importing the model take a look at model importer logs for more info";
                clientErrors.put("504", msg);
                log.error(msg);
            }
            else{
                successImport = true;
                log.info("It seems that model-importer was correctly called using this URL: {}", importModelURLStr);
            }

            client.close();
        } catch (MalformedURLException mlURLex) {
            String msg = "It seems like the provided URL is not properly formed";
            clientErrors.put("500", msg);
            log.error(msg, mlURLex);
        } catch (IOException ioex) {
            String msg = "An IOException was generated check the server side logs for more details...";
            clientErrors.put("503", msg);
            log.error(msg, ioex);
        }

        return successImport;
    }

    public static String createHashedString(String randString, int length){
        MessageDigest digest = null;
        try {
            digest = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            log.error("An error occurred while getting the hash code", e);
            return null;
        }

        byte[] encodedHash = digest.digest(randString.getBytes(StandardCharsets.UTF_8));

        return Utils.bytesToHex(encodedHash).substring(0, length);
    }

    private File copyModelLibrary(File modelType) throws IOException{
        Path boilerPlateDir = Paths.get(modelType.getPath());
        File modelDir = new File(tmpSubDir, "model_dir");
        FileUtils.copyDirectory(boilerPlateDir.toFile(),
                modelDir,
                pathname -> !pathname.getAbsolutePath().contains(appConfigValues.getImporterResDir()));

        return modelDir;
    }

    public File copyAssetBundleDir(File modelType) throws IOException {
        File tmpAssetDir = new File(tmpSubDir, "assets");
        Path modelOnePath = Paths.get(tmpAssetDir.getAbsolutePath(),
                appConfigValues.getImporterResDir(),
                appConfigValues.getImporterRootDir(),
                appConfigValues.getImporterModelDir());
        Path assetBundle = Paths.get(modelType.getPath(), appConfigValues.getImporterResDir());
        FileUtils.copyDirectory(assetBundle.toFile(), modelOnePath.toFile());
        Path assetConfigPath = Paths.get(modelOnePath.toString(), appConfigValues.getModelConfigName());
        boolean configDeleted = assetConfigPath.toFile().delete();
        if (configDeleted){
            log.info("The config file was correctly deleted from the temporary location");
        }
        else {
            String msg = "There was a problem deleting the " + appConfigValues.getModelConfigName() + " from the temporary location";
            clientErrors.put("500", msg);
            log.error(msg);
            return null;
        }

        return tmpAssetDir;
    }

    private void copyModelFile(File resourcesFolderFile, File assetDirFile) throws IOException {
        File modelFile = new File(resourcesFolderFile, appConfigValues.getModelFileName());
        Path modelVersionPath = Paths.get(assetDirFile.getAbsolutePath(),
                appConfigValues.getImporterResDir(),
                appConfigValues.getImporterRootDir(),
                appConfigValues.getImporterModelDir(),
                modelVersion);

        File destModelFile = new File(modelVersionPath.toFile(), appConfigValues.getModelFileName());
        if (destModelFile.exists())
            destModelFile.delete();
        FileUtils.copyFile(modelFile, destModelFile);

        File mainModelFile = new File(tempModelDir, appConfigValues.getModelFileName());
        if (mainModelFile.exists())
            mainModelFile.delete();
        FileUtils.copyFile(modelFile, mainModelFile);

        final File[] files = resourcesFolderFile.listFiles((dir, name) -> name.matches( ".*model\\.yaml.*" ));
        for ( final File file : files ) {
            if ( !file.delete() ) {
                log.error("It was not possible removing: " + file.getAbsolutePath() );
            }
        }
    }

    private void copyModelArtifacts(File artifactFolderFile, File modelDirFile, String artifactDirName) throws IOException {
        FileUtils.copyDirectory(artifactFolderFile,
                Paths.get(modelDirFile.toString(), appConfigValues.getModelScriptDir(), artifactDirName).toFile());
    }

    private void retrieveModelInfo(File modelFile) throws FileNotFoundException {
        InputStream inputStream = new FileInputStream(modelFile);

        Yaml yaml = new Yaml();
        Map<String, Object> modelInfo = (Map<String, Object>) yaml.load(inputStream);
        modelVersion = (String) modelInfo.getOrDefault("version", "0.0.1");
        modelName = (String) modelInfo.get("name");
        try {
            inputStream.close();
        } catch (IOException ioex) {
            log.error("There was an issue closing the model metadata file.", ioex);
        }
    }

    private void createConfigFile(File assetDirFile) throws IOException {
        String strToHash = hashBase + modelName;
        String hashedString = createHashedString(strToHash, 10);
        imageName = "converted-model-" + hashedString;
        modelId = hashedString;
        AssetConfig assetConfig = new AssetConfig();
        assetConfig.setId(modelId);
        assetConfig.setLastVersion(modelVersion);
        DockerRepository repoInfo = new DockerRepository();
        repoInfo.setHost(ecrURI);
        repoInfo.setName(imageName);
        repoInfo.setPrefix(ecrRepo);
        assetConfig.setDockerRepository(repoInfo);
        Yaml yaml = new Yaml();
        Path configYamlPath = Paths.get(assetDirFile.toString(),
                appConfigValues.getImporterResDir(),
                appConfigValues.getImporterRootDir(),
                appConfigValues.getImporterModelDir(),
                appConfigValues.getModelConfigName());
        FileWriter configYamlFile = new FileWriter(configYamlPath.toString());
        String assetConfigStr = yaml.dumpAs(assetConfig, Tag.MAP, DumperOptions.FlowStyle.BLOCK);
        configYamlFile.write(assetConfigStr);
        configYamlFile.close();
    }

    private byte[] getBinaryAssetBundle(S3ArchiveHelper archiveHelper, File assetDirFile) throws IOException {
        Path allModelsPath = Paths.get(assetDirFile.getAbsolutePath(),  appConfigValues.getImporterResDir());
        return archiveHelper.createArchiveFile("model_to_import.tar.gz", allModelsPath.toFile());
    }

    public void setValidations(Map<Validator, Map<AppVariable, String>> validations) {
        this.validations = validations;
    }

    public void setVerifications(Map<String, AssetVerifierDTO> verifications) {
        this.verifications = verifications;
    }

    public Map<String, AssetVerifierDTO> getVerifications() {
        return verifications;
    }

    public File getTempModelDir() {
        return tempModelDir;
    }

    public void setTempModelDir(File tempModelDir) {
        this.tempModelDir = tempModelDir;
    }

    public void setImageName(String imageName) { this.imageName = imageName; }

    public File getTempSubdir() {
        return tmpSubDir;
    }

    public String getModelId() {
        return modelId;
    }

    public String getImageName() {
        return imageName;
    }

    public String getEcrURL() {
        return ecrURL;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public Map<String, String> getClientErrors() {
        return clientErrors;
    }

    public Configuration getAppConfigValues() {
        return appConfigValues;
    }
}
