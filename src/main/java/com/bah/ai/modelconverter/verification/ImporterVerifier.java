package com.bah.ai.modelconverter.verification;

import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@Slf4j
public class ImporterVerifier extends AssetVerifier<String> {
    public ImporterVerifier() {
        this.assetName = "ImporterURL";
    }

    @Override
    public boolean verify(Map<String, String> params) {
        boolean verified = false;
        String importerHost = params.get(AppVariable.IMPORTER_HOST.getAppVarName());
        String importerPortName = AppVariable.IMPORTER_PORT.getAppVarName();
        if (params.containsKey(importerPortName)) {
            String importerPort = params.get(importerPortName);
            this.asset = String.format("http://%s:%s/", importerHost, importerPort);
        } else {
            this.asset = String.format("http://%s/", importerHost);
        }
        String requestUrl = this.asset + "status";
        try {
            CloseableHttpClient client = HttpClients.createDefault();
            HttpGet request = new HttpGet(requestUrl);
            CloseableHttpResponse response = client.execute(request);
            StringBuilder content;
            try (BufferedReader br = new BufferedReader(new InputStreamReader(response.getEntity().getContent()))) {
                String line;
                content = new StringBuilder();
                while ((line = br.readLine()) != null) {
                    content.append(line);
                    content.append(System.lineSeparator());
                }
            }
            if (content.toString().contains("Importer server working ")) {
                log.info("Response from model importer: " + content.toString());
                verified = true;
                log.info("The importer seems to be running and ready to accept connections at " + requestUrl);
            } else {
                this.failureReason = "There is a problem getting the expected message";
                log.error(this.failureReason);
            }

            client.close();
        } catch (MalformedURLException mURLex) {
            this.failureReason = "There has been a problem with the importer URL";
            log.error(this.failureReason, mURLex);
        } catch (ProtocolException protocolEx) {
            this.failureReason = "It is not possible to create a connection to the importer service";
            log.error(this.failureReason, protocolEx);
        } catch (IOException ioEx) {
            this.failureReason = "There was a problem opening a stream to verify status. Attempted to make a GET request to " + requestUrl;
            log.error(this.failureReason, ioEx);
        }

        return verified;
    }
}
