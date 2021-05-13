package com.bah.ai.modelconverter.verification;

import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.AmazonECRClientBuilder;
import com.amazonaws.services.ecr.model.DescribeRepositoriesRequest;
import com.amazonaws.services.ecr.model.DescribeRepositoriesResult;
import com.amazonaws.services.ecr.model.Repository;
import com.bah.ai.modelconverter.AppVariable;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;

@Slf4j
public class ECRVerifier extends AssetVerifier<AmazonECR> {
    public ECRVerifier() {
        this.assetName = "ECR";
    }

    @Override
    public boolean verify(Map<String, String> parameters) {
        boolean verified = false;
        Region region = Regions.getCurrentRegion() != null ? Regions.getCurrentRegion() : Region.getRegion(Regions.US_EAST_1);
        try {
            this.asset = AmazonECRClientBuilder.standard().withRegion(region.getName()).build();
            DescribeRepositoriesRequest request = new DescribeRepositoriesRequest();
            DescribeRepositoriesResult response = this.asset.describeRepositories(request);
            String ecrRepoName = parameters.get(AppVariable.ECR_REPO.getAppVarName());
            boolean repoFound = false;
            for (Repository repo : response.getRepositories()) {
                if (repo.getRepositoryName().equals(ecrRepoName)) {
                    repoFound = true;
                    break;
                }
            }
            if (repoFound)
                log.info("ECR endpoint verified and ready for usage in next steps");
            else {
                this.failureReason = "It seemed that the repo, " + ecrRepoName + " was not found";
                log.error(this.failureReason);
            }
            verified = repoFound;
        } catch (Exception e) {
            this.failureReason = e.getMessage();
            log.error("Error while trying to get access to ECR, verify that your AWS keys or profile has access to this service.");
        }
        return verified;
    }
}
