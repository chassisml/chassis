package com.bah.ai.modelconverter.api.controller;

import com.bah.ai.modelconverter.api.dto.OperationResponseDTO;
import com.bah.ai.modelconverter.api.service.ModelConverterService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class ModelConverterServiceController {
    private final ModelConverterService converterService = new ModelConverterService();

    @GetMapping(value = "/env-status")
    public OperationResponseDTO getEnvironmentStatus(){
        return converterService.checkEnvironment();
    }

    @GetMapping(value = "/check-endpoints")
    public OperationResponseDTO checkIntegrations(@RequestParam final String aws_key_id,
                                                  @RequestParam final String aws_access_key,
                                                  @RequestParam final String s3Bucket,
                                                  @RequestParam final String weightsPath,
                                                  @RequestParam final String resourcesPath,
                                                  @RequestParam final String platform,
                                                  @RequestParam final String model_type){
        return converterService.checkIntegrations(aws_key_id, aws_access_key, s3Bucket, weightsPath, resourcesPath, platform, model_type);
    }

    @GetMapping(value = "/run-converter")
    public OperationResponseDTO runConverter(@RequestParam final String aws_key_id,
                                             @RequestParam final String aws_access_key,
                                             @RequestParam final String s3Bucket,
                                             @RequestParam final String weightsPath,
                                             @RequestParam final String resourcesPath,
                                             @RequestParam final String platform,
                                             @RequestParam final String model_type){
        return converterService.executeConverter(aws_key_id, aws_access_key, s3Bucket, weightsPath, resourcesPath, platform, model_type);
    }
}
