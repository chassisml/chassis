package com.bah.ai.modelconverter.dto;

import com.bah.ai.modelconverter.verification.AssetVerifier;
import lombok.Data;

import java.util.Map;

@Data
public class AssetVerifierDTO {
    private AssetVerifier verifierObj;

    private Map<String, String> verifierSettings;

}
