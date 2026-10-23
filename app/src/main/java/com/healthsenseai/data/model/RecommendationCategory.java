package com.healthsenseai.data.model;

import com.google.gson.annotations.SerializedName;

/**
 * Recommendation category for a family member.
 */
public enum RecommendationCategory {
    @SerializedName(value = "RECOMMENDED", alternate = {"SUITABLE", "SAFE"})
    SUITABLE("Suitable", "Safe to consume based on health profile"),
    
    @SerializedName(value = "CAUTION", alternate = {"MODERATE", "CONSUME_WITH_CAUTION"})
    CAUTION("Consume with Caution", "Moderate risk factors detected; consume in strict moderation"),
    
    @SerializedName(value = "AVOID", alternate = {"NOT_RECOMMENDED", "HIGH_RISK"})
    NOT_RECOMMENDED("Not Recommended", "High risk factors or allergens detected; avoid consumption");

    private final String displayName;
    private final String description;

    RecommendationCategory(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }
}
