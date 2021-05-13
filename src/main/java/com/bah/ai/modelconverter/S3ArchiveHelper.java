package com.bah.ai.modelconverter;

import com.amazonaws.services.s3.model.S3Object;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.rauschig.jarchivelib.ArchiveFormat;
import org.rauschig.jarchivelib.Archiver;
import org.rauschig.jarchivelib.ArchiverFactory;
import org.rauschig.jarchivelib.CompressionType;

import java.io.File;
import java.io.IOException;

@Slf4j
public class S3ArchiveHelper {
    private static Archiver ARCHIVER = ArchiverFactory.createArchiver(ArchiveFormat.TAR, CompressionType.GZIP);

    private File archiveFolder;
    private File assetDir;
    private S3Object cloudObjectRef;

    public S3ArchiveHelper(S3Object s3Object, File tmpSubdir) {
        this.cloudObjectRef = s3Object;
        archiveFolder = new File(tmpSubdir, "archives");
        log.info("Folder: {}", archiveFolder);
    }

    public File downloadFile() throws IOException {
        String cloudObjKey = cloudObjectRef.getKey();
        File targzFile = new File(archiveFolder, cloudObjKey.substring(cloudObjKey.indexOf("/")));
        FileUtils.copyInputStreamToFile(cloudObjectRef.getObjectContent(), targzFile);
        return targzFile;
    }

    public File extractCompressedArchive(File tarZippedFile, String destDirectory) throws IOException {
        File archiveDestDir = new File(archiveFolder, destDirectory);
        ARCHIVER.extract(tarZippedFile, archiveDestDir);
        return archiveDestDir;
    }

    public byte[] createArchiveFile(String archiveFileName, File allModelsDir) throws IOException {
        assetDir = allModelsDir.getParentFile();
        ARCHIVER.create(archiveFileName, assetDir, allModelsDir);
        return FileUtils.readFileToByteArray(new File(assetDir, archiveFileName));
    }

    public File getAssetDir() {
        return assetDir;
    }
}
