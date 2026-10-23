package com.healthsenseai.data.model;

import java.io.Serializable;
import java.util.List;

/**
 * Payload sent to the Python FastAPI backend for AI-powered family food recommendations.
 */
public class RecommendationRequest implements Serializable {

    private FoodProduct foodProduct;
    private List<FamilyMember> familyMembers;
    private long timestamp;

    public RecommendationRequest() {
        this.timestamp = System.currentTimeMillis();
    }

    public RecommendationRequest(FoodProduct foodProduct, List<FamilyMember> familyMembers) {
        this.foodProduct = foodProduct;
        this.familyMembers = familyMembers;
        this.timestamp = System.currentTimeMillis();
    }

    public FoodProduct getFoodProduct() {
        return foodProduct;
    }

    public void setFoodProduct(FoodProduct foodProduct) {
        this.foodProduct = foodProduct;
    }

    public List<FamilyMember> getFamilyMembers() {
        return familyMembers;
    }

    public void setFamilyMembers(List<FamilyMember> familyMembers) {
        this.familyMembers = familyMembers;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }
}
