package com.healthsenseai.data.model;

import com.healthsenseai.utils.Constants;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * Response received from the recommendation engine (Python FastAPI or local engine).
 */
public class RecommendationResponse implements Serializable {

    private String barcode;
    private String productName;
    private List<FamilyRecommendation> recommendations = new ArrayList<>();
    private String overallVerdict;
    private long analyzedAt;
    private String disclaimer = Constants.MEDICAL_DISCLAIMER;
    private String foodGrade;
    private double foodQualityScore;
    private String activeModel;
    private String source; // "REMOTE_BACKEND" or "LOCAL_FALLBACK"
    private String assessmentConfidence; // "HIGH", "MEDIUM", "LOW"
    private String frequencyRecommendation; // "DAILY", "OCCASIONAL", "LIMIT", "AVOID"

    public RecommendationResponse() {
        this.analyzedAt = System.currentTimeMillis();
    }

    public RecommendationResponse(String barcode, String productName, List<FamilyRecommendation> recommendations) {
        this.barcode = barcode;
        this.productName = productName;
        this.recommendations = recommendations;
        this.analyzedAt = System.currentTimeMillis();
        this.disclaimer = Constants.MEDICAL_DISCLAIMER;
    }

    public String getBarcode() {
        return barcode;
    }

    public void setBarcode(String barcode) {
        this.barcode = barcode;
    }

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public List<FamilyRecommendation> getRecommendations() {
        return recommendations != null ? recommendations : new ArrayList<>();
    }

    public void setRecommendations(List<FamilyRecommendation> recommendations) {
        this.recommendations = recommendations;
    }

    public String getOverallVerdict() {
        return overallVerdict;
    }

    public void setOverallVerdict(String overallVerdict) {
        this.overallVerdict = overallVerdict;
    }

    public long getAnalyzedAt() {
        return analyzedAt;
    }

    public void setAnalyzedAt(long analyzedAt) {
        this.analyzedAt = analyzedAt;
    }

    public String getDisclaimer() {
        return disclaimer;
    }

    public void setDisclaimer(String disclaimer) {
        this.disclaimer = disclaimer;
    }

    public String getFoodGrade() {
        return foodGrade;
    }

    public void setFoodGrade(String foodGrade) {
        this.foodGrade = foodGrade;
    }

    public double getFoodQualityScore() {
        return foodQualityScore;
    }

    public void setFoodQualityScore(double foodQualityScore) {
        this.foodQualityScore = foodQualityScore;
    }

    public String getActiveModel() {
        return activeModel;
    }

    public void setActiveModel(String activeModel) {
        this.activeModel = activeModel;
    }

    public String getSource() {
        return source != null ? source : "REMOTE_BACKEND";
    }

    public void setSource(String source) {
        this.source = source;
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
}
