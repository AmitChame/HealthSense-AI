package com.healthsenseai.data.model;

/**
 * Risk level assigned to a food product evaluation.
 */
public enum RiskLevel {
    LOW("Low Risk"),
    MODERATE("Moderate Risk"),
    HIGH("High Risk");

    private final String displayName;

    RiskLevel(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}
