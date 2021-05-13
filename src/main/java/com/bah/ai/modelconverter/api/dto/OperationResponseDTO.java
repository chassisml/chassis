package com.bah.ai.modelconverter.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;

import java.util.LinkedList;
import java.util.List;

@AllArgsConstructor
@NoArgsConstructor
@EqualsAndHashCode
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
public class OperationResponseDTO {
    private List<ResponseEntry> responseEntries = new LinkedList<>();
    private SuccessEntry successEntry;

    @Builder
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ResponseEntry {
        private String httpCode;
        private String message;
    }

    @Builder
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class SuccessEntry {
        private String modelId;
        private String modelName;
        private String modelVersion;
        private String ecrURL;
        private String modelURL;
    }
}
