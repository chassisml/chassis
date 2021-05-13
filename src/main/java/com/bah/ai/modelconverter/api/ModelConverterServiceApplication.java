package com.bah.ai.modelconverter.api;

import com.bah.ai.modelconverter.AppVariable;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

@SpringBootApplication(
        scanBasePackages = {"com.bah.ai.modelconverter.api.controller"}
)
public class ModelConverterServiceApplication {

    public static void main(String[] args) throws IOException {
        String credFileName = "/kaniko/.aws/credentials";
        BufferedWriter credWriter = new BufferedWriter(new FileWriter(credFileName));
        credWriter.write("[default]\n");
        credWriter.write(String.format("aws_access_key_id = %s\n", System.getenv(AppVariable.AWS_KEY_ID.getAppVarName())));
        credWriter.write(String.format("aws_secret_access_key = %s\n", System.getenv(AppVariable.AWS_SECRET_KEY.getAppVarName())));
        credWriter.close();

        String ecrURI = System.getenv(AppVariable.ECR_REGISTRY.getAppVarName());
        String ecrRegistry = ecrURI.replace("https://", "");

        String configFileName = "/kaniko/.docker/config.json";
        BufferedWriter configWriter = new BufferedWriter(new FileWriter(configFileName));
        configWriter.write("{\n");
        configWriter.write("\t\"credsStore\":\"ecr-login\",\n");
        configWriter.write("\t\"credHelpers\": {\n");
        configWriter.write(String.format("\t\t\"%s\": \"ecr-login\"\n", ecrRegistry));
        configWriter.write("\t}\n");
        configWriter.write("}\n");
        configWriter.close();

        SpringApplication.run(ModelConverterServiceApplication.class, args);
    }

}
