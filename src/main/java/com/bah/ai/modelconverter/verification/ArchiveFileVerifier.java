package com.bah.ai.modelconverter.verification;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.S3Object;
import com.bah.ai.modelconverter.AppVariable;
import com.bah.ai.modelconverter.S3ArchiveHelper;
import com.bah.ai.modelconverter.Utils;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.io.IOException;
import java.util.Map;

@Slf4j
public class ArchiveFileVerifier extends AssetVerifier<File> {
    private AssetVerifier<AmazonS3> s3Verifier;
    private S3ArchiveHelper archiveHelper;
    private File temporarySubdir;

    public ArchiveFileVerifier(String fileName, AssetVerifier s3VerifierObj, File tmpSubdir) {
        this.assetName += "_" + fileName;
        this.s3Verifier = s3VerifierObj;
        temporarySubdir = tmpSubdir;
    }

    @Override
    public boolean verify(Map<String, String> parameters) {
        boolean verified = false;
        String assetDesc = parameters.get("ASSET_DESC");
        String assetPath = parameters.get("ASSET_PATH");
        String bucketName = parameters.get(AppVariable.SAGEMAKER_BUCKET.getAppVarName());

        try {
            S3Object s3ObjectArchive = s3Verifier.getAsset().getObject(bucketName, assetPath);
            archiveHelper = new S3ArchiveHelper(s3ObjectArchive, temporarySubdir);
            File localPathArchive = archiveHelper.downloadFile();
            if (localPathArchive.getName().endsWith(".tar.gz") && localPathArchive.isFile()) {
                if (Utils.isGZipped(localPathArchive)) {
                    try {
                        this.asset = archiveHelper.extractCompressedArchive(localPathArchive, assetName);
                        verified = true;
                        log.info(String.format("Verification of the model assets %s inside '%s' were successful", assetDesc, localPathArchive.getAbsolutePath()));
                    } catch (IOException ioe) {
                        this.failureReason = "Seems like the tar gzipped file " + localPathArchive.getName() + " are not in the right format";
                        log.error(this.failureReason, ioe);
                    }
                } else {
                    this.failureReason = "It seems like the specified archive file is not in gzip format";
                    log.error(this.failureReason);
                }
            } else {
                this.failureReason = "The " + assetDesc + " archive value must end in .tar.gz and be a file";
                log.error(this.failureReason);
            }
        } catch (IOException ioex) {
            this.failureReason = "An IO error has happened while downloading " + assetDesc + " object";
            log.error(this.failureReason, ioex);
        } catch (Exception e) {
            this.failureReason = "A general exception was thrown while processing " + assetDesc + " object";
            log.error(this.failureReason, e);
        }

        return verified;
    }

    public S3ArchiveHelper getArchiveHelper() {
        return archiveHelper;
    }
}
