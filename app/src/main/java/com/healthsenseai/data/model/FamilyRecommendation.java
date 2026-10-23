package com.healthsenseai.data.model;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * Individual assessment result for a specific family member against a food product.
 */
public class FamilyRecommendation implements Serializable {

    private String familyMemberId;
    private String familyMemberName;
    private int familyMemberAge;
    private String healthSummary;
    private RecommendationCategory category;
    private RiskLevel riskLevel;
    private double riskScore; // 0.0 to 100.0
    private String summaryReason;
    private List<HealthFactor> healthFactors = new ArrayList<>();
    private List<String> warnings = new ArrayList<>();
    private String foodGrade;
    private List<String> ingredientConcerns = new ArrayList<>();
    private String modelName;
    private double confidence;
    private String assessmentConfidence;
    private String frequencyRecommendation;
    private String lifeStage;

    public FamilyRecommendation() {
    }

    public FamilyRecommendation(String familyMemberId, String familyMemberName, RecommendationCategory category, RiskLevel riskLevel, String summaryReason) {
        this.familyMemberId = familyMemberId;
        this.familyMemberName = familyMemberName;
        this.category = category;
        this.riskLevel = riskLevel;
        this.summaryReason = summaryReason;
    }

    public String getFamilyMemberId() {
        return familyMemberId;
    }

    public void setFamilyMemberId(String familyMemberId) {
        this.familyMemberId = familyMemberId;
    }

    public String getFamilyMemberName() {
        return familyMemberName;
    }

    public void setFamilyMemberName(String familyMemberName) {
        this.familyMemberName = familyMemberName;
    }

    public int getFamilyMemberAge() {
        return familyMemberAge;
    }

    public void setFamilyMemberAge(int familyMemberAge) {
        this.familyMemberAge = familyMemberAge;
    }

    public String getHealthSummary() {
        return healthSummary != null ? healthSummary : "";
    }

    public void setHealthSummary(String healthSummary) {
        this.healthSummary = healthSummary;
    }

    public RecommendationCategory getCategory() {
        return category != null ? category : RecommendationCategory.SUITABLE;
    }

    public void setCategory(RecommendationCategory category) {
        this.category = category;
    }

    public RiskLevel getRiskLevel() {
        return riskLevel != null ? riskLevel : RiskLevel.LOW;
    }

    public void setRiskLevel(RiskLevel riskLevel) {
        this.riskLevel = riskLevel;
    }

    public double getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(double riskScore) {
        this.riskScore = riskScore;
    }

    public String getSummaryReason() {
        return summaryReason;
    }

    public void setSummaryReason(String summaryReason) {
        this.summaryReason = summaryReason;
    }

    public List<HealthFactor> getHealthFactors() {
        return healthFactors != null ? healthFactors : new ArrayList<>();
    }

    public void setHealthFactors(List<HealthFactor> healthFactors) {
        this.healthFactors = healthFactors;
    }

    public List<String> getWarnings() {
        return warnings != null ? warnings : new ArrayList<>();
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public String getFoodGrade() {
        return foodGrade;
    }

    public void setFoodGrade(String foodGrade) {
        this.foodGrade = foodGrade;
    }

    public List<String> getIngredientConcerns() {
        return ingredientConcerns != null ? ingredientConcerns : new ArrayList<>();
    }

    public void setIngredientConcerns(List<String> ingredientConcerns) {
        this.ingredientConcerns = ingredientConcerns;
    }

    public String getModelName() {
        return modelName;
    }

    public void setModelName(String modelName) {
        this.modelName = modelName;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public String getAssessmentConfidence() {
        return assessmentConfidence != null ? assessmentConfidence : "HIGH";
    }

    public void setAssessmentConfidence(String assessmentConfidence) {
        this.assessmentConfidence = assessmentConfidence;
    }

    public String getFrequencyRecommendation() {
        return frequencyRecommendation != null ? frequencyRecommendation : "OCCASIONAL";
    }

    public void setFrequencyRecommendation(String frequencyRecommendation) {
        this.frequencyRecommendation = frequencyRecommendation;
    }

    public String getLifeStage() {
        return lifeStage != null ? lifeStage : "ADULT";
    }

    public void setLifeStage(String lifeStage) {
        this.lifeStage = lifeStage;
    }
}
