package com.bah.ai.modelconverter;

import lombok.extern.slf4j.Slf4j;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.GZIPInputStream;

@Slf4j
public class Utils {

    public static String readFileAsString(Path filepath) {
        String text = "";
        try {
            text = new String(Files.readAllBytes(filepath));
        } catch (IOException e) {
            log.error("Error while reading all bytes from file " + filepath, e);
        }
        return text;
    }

    public static boolean isGZipped(InputStream in) {
        if (!in.markSupported()) {
            in = new BufferedInputStream(in);
        }
        in.mark(2);
        int magic;
        try {
            magic = in.read() & 0xff | ((in.read() << 8) & 0xff00);
            in.reset();
        } catch (IOException e) {
            e.printStackTrace(System.err);
            return false;
        }
        return magic == GZIPInputStream.GZIP_MAGIC;
    }

    public static boolean isGZipped(File f) {
        int magic = 0;
        try {
            RandomAccessFile raf = new RandomAccessFile(f, "r");
            magic = raf.read() & 0xff | ((raf.read() << 8) & 0xff00);
            raf.close();
        } catch (Throwable e) {
            e.printStackTrace(System.err);
        }
        return magic == GZIPInputStream.GZIP_MAGIC;
    }

    public static String bytesToHex(byte[] hash) {
        StringBuilder hexString = new StringBuilder(2 * hash.length);
        for (int i = 0; i < hash.length; i++) {
            String hex = Integer.toHexString(0xff & hash[i]);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }
}
