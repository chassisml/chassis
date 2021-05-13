package com.bah.ai.modelconverter.verification;

import java.util.Map;
import java.util.Objects;

public abstract class AssetVerifier<T> {
    protected String assetName;
    protected String failureReason;
    protected T asset;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AssetVerifier verifier = (AssetVerifier) o;
        return assetName.equals(verifier.assetName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(assetName);
    }

    public String getFailureReason() {
        return failureReason;
    }

    public T getAsset() {
        return asset;
    }

    public abstract boolean verify(Map<String, String> parameters);
}
