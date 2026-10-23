package com.healthsenseai.data.model;

import com.google.firebase.firestore.DocumentId;
import com.google.firebase.firestore.ServerTimestamp;
import java.io.Serializable;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * Scan history item stored in Firestore at 'users/{userId}/scanHistory/{scanId}'.
 */
public class ScanHistoryItem implements Serializable {

    @DocumentId
    private String id;
    private String userId;
    private String barcode;
    private String productName;
    private String brand;
    private String imageUrl;
    private Map<String, String> memberSuitability = new HashMap<>(); // MemberName -> SUITABLE / CAUTION / NOT_RECOMMENDED
    private FoodProduct foodProduct;
    private RecommendationResponse recommendationResponse;

    @ServerTimestamp
    private Date scannedAt;

    private long timestampMillis;

    public ScanHistoryItem() {
        this.timestampMillis = System.currentTimeMillis();
    }

    public ScanHistoryItem(String userId, FoodProduct foodProduct, RecommendationResponse recommendationResponse) {
        this.userId = userId;
        this.foodProduct = foodProduct;
        this.recommendationResponse = recommendationResponse;
        if (foodProduct != null) {
            this.barcode = foodProduct.getBarcode();
            this.productName = foodProduct.getProductName();
            this.brand = foodProduct.getBrand();
            this.imageUrl = foodProduct.getImageUrl();
        }
        if (recommendationResponse != null && recommendationResponse.getRecommendations() != null) {
            for (FamilyRecommendation rec : recommendationResponse.getRecommendations()) {
                if (rec.getFamilyMemberName() != null && rec.getCategory() != null) {
                    this.memberSuitability.put(rec.getFamilyMemberName(), rec.getCategory().name());
                }
            }
        }
        this.timestampMillis = System.currentTimeMillis();
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getBarcode() {
        return barcode;
    }

    public void setBarcode(String barcode) {
        this.barcode = barcode;
    }

    public String getProductName() {
        return productName != null ? productName : "Unknown Product";
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getBrand() {
        return brand != null ? brand : "";
    }

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public Map<String, String> getMemberSuitability() {
        return memberSuitability != null ? memberSuitability : new HashMap<>();
    }

    public void setMemberSuitability(Map<String, String> memberSuitability) {
        this.memberSuitability = memberSuitability;
    }

    public FoodProduct getFoodProduct() {
        return foodProduct;
    }

    public void setFoodProduct(FoodProduct foodProduct) {
        this.foodProduct = foodProduct;
    }

    public RecommendationResponse getRecommendationResponse() {
        return recommendationResponse;
    }

    public void setRecommendationResponse(RecommendationResponse recommendationResponse) {
        this.recommendationResponse = recommendationResponse;
    }

    public Date getScannedAt() {
        return scannedAt;
    }

    public void setScannedAt(Date scannedAt) {
        this.scannedAt = scannedAt;
    }

    public long getTimestampMillis() {
        return timestampMillis > 0 ? timestampMillis : (scannedAt != null ? scannedAt.getTime() : System.currentTimeMillis());
    }

    public void setTimestampMillis(long timestampMillis) {
        this.timestampMillis = timestampMillis;
    }
}
