package com.healthsenseai.data.model;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * Domain model representing a packaged food product scanned via barcode or queried via API.
 */
public class FoodProduct implements Serializable {

    @SerializedName("barcode")
    private String barcode;

    @SerializedName("productName")
    private String productName;

    @SerializedName("brand")
    private String brand;

    @SerializedName("ingredients")
    private String ingredients;

    @SerializedName("servingSize")
    private String servingSize;

    @SerializedName("imageUrl")
    private String imageUrl;
    
    @SerializedName("nutriScore")
    private String nutritionGrade;
    
    @SerializedName("novaGroup")
    private String novaGroup;

    @SerializedName("allergens")
    private List<String> allergens = new ArrayList<>();

    @SerializedName("categories")
    private List<String> categories = new ArrayList<>();

    @SerializedName("nutriments")
    private Nutriments nutriments = new Nutriments();

    public FoodProduct() {
    }

    public FoodProduct(String barcode, String productName, String brand) {
        this.barcode = barcode;
        this.productName = productName;
        this.brand = brand;
    }

    public String getBarcode() {
        return barcode;
    }

    public void setBarcode(String barcode) {
        this.barcode = barcode;
    }

    public String getProductName() {
        return (productName != null && !productName.trim().isEmpty()) ? productName : "Unknown Product";
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getBrand() {
        return (brand != null && !brand.trim().isEmpty()) ? brand : "Unknown Brand";
    }

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public String getIngredients() {
        return (ingredients != null && !ingredients.trim().isEmpty()) ? ingredients : "No ingredients information listed";
    }

    public void setIngredients(String ingredients) {
        this.ingredients = ingredients;
    }

    public String getServingSize() {
        return (servingSize != null && !servingSize.trim().isEmpty()) ? servingSize : "100g";
    }

    public void setServingSize(String servingSize) {
        this.servingSize = servingSize;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public String getNutritionGrade() {
        return nutritionGrade;
    }

    public void setNutritionGrade(String nutritionGrade) {
        this.nutritionGrade = nutritionGrade;
    }

    public String getNovaGroup() {
        return novaGroup;
    }

    public void setNovaGroup(String novaGroup) {
        this.novaGroup = novaGroup;
    }

    public List<String> getAllergens() {
        return allergens != null ? allergens : new ArrayList<>();
    }

    public void setAllergens(List<String> allergens) {
        this.allergens = allergens;
    }

    public List<String> getCategories() {
        return categories != null ? categories : new ArrayList<>();
    }

    public void setCategories(List<String> categories) {
        this.categories = categories;
    }

    public Nutriments getNutriments() {
        return nutriments != null ? nutriments : new Nutriments();
    }

    public void setNutriments(Nutriments nutriments) {
        this.nutriments = nutriments;
    }
}
