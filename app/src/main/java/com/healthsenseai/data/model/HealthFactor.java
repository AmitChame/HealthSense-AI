package com.healthsenseai.data.model;

import java.io.Serializable;

/**
 * Represents a key nutrient, ingredient, or allergen factor flagged during analysis.
 */
public class HealthFactor implements Serializable {

    private String name;
    private RiskLevel impact;
    private String description;
    private boolean isAllergen;
    private String detectedValue;
    private String thresholdValue;

    public HealthFactor() {
    }

    public HealthFactor(String name, RiskLevel impact, String description) {
        this.name = name;
        this.impact = impact;
        this.description = description;
        this.isAllergen = false;
    }

    public HealthFactor(String name, RiskLevel impact, String description, boolean isAllergen, String detectedValue, String thresholdValue) {
        this.name = name;
        this.impact = impact;
        this.description = description;
        this.isAllergen = isAllergen;
        this.detectedValue = detectedValue;
        this.thresholdValue = thresholdValue;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public RiskLevel getImpact() {
        return impact != null ? impact : RiskLevel.LOW;
    }

    public void setImpact(RiskLevel impact) {
        this.impact = impact;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public boolean isAllergen() {
        return isAllergen;
    }

    public void setAllergen(boolean allergen) {
        isAllergen = allergen;
    }

    public String getDetectedValue() {
        return detectedValue;
    }

    public void setDetectedValue(String detectedValue) {
        this.detectedValue = detectedValue;
    }

    public String getThresholdValue() {
        return thresholdValue;
    }

    public void setThresholdValue(String thresholdValue) {
        this.thresholdValue = thresholdValue;
    }
}
