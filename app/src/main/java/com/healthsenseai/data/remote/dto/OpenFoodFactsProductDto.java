package com.healthsenseai.data.remote.dto;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

/**
 * DTO mapping OpenFoodFacts 'product' JSON object.
 */
public class OpenFoodFactsProductDto implements Serializable {

    @SerializedName("code")
    private String code;

    @SerializedName("product_name")
    private String productName;

    @SerializedName("product_name_en")
    private String productNameEn;

    @SerializedName("brands")
    private String brands;

    @SerializedName("ingredients_text")
    private String ingredientsText;

    @SerializedName("ingredients_text_en")
    private String ingredientsTextEn;

    @SerializedName("serving_size")
    private String servingSize;

    @SerializedName("image_url")
    private String imageUrl;

    @SerializedName("image_front_url")
    private String imageFrontUrl;

    @SerializedName("nutrition_grades")
    private String nutritionGrades;

    @SerializedName("nova_group")
    private String novaGroup;

    @SerializedName("allergens_tags")
    private List<String> allergensTags;

    @SerializedName("allergens_hierarchy")
    private List<String> allergensHierarchy;

    @SerializedName("categories_tags")
    private List<String> categoriesTags;

    @SerializedName("nutriments")
    private OpenFoodFactsNutrimentsDto nutriments;

    public String getCode() {
        return code;
    }

    public String getResolvedProductName() {
        if (productName != null && !productName.trim().isEmpty()) {
            return productName;
        } else if (productNameEn != null && !productNameEn.trim().isEmpty()) {
            return productNameEn;
        }
        return "Packaged Food Product";
    }

    public String getBrands() {
        return brands != null ? brands : "Standard Brand";
    }

    public String getResolvedIngredients() {
        if (ingredientsText != null && !ingredientsText.trim().isEmpty()) {
            return ingredientsText;
        } else if (ingredientsTextEn != null && !ingredientsTextEn.trim().isEmpty()) {
            return ingredientsTextEn;
        }
        return "Ingredients list not provided by packaging data.";
    }

    public String getServingSize() {
        return servingSize != null ? servingSize : "100g";
    }

    public String getResolvedImageUrl() {
        if (imageUrl != null && !imageUrl.trim().isEmpty()) {
            return imageUrl;
        }
        return imageFrontUrl;
    }

    public String getNutritionGrades() {
        return nutritionGrades != null ? nutritionGrades.toUpperCase() : "N/A";
    }

    public String getNovaGroup() {
        return novaGroup;
    }

    public void setNovaGroup(String novaGroup) {
        this.novaGroup = novaGroup;
    }

    public List<String> getCleanAllergens() {
        List<String> cleaned = new ArrayList<>();
        List<String> raw = allergensTags != null ? allergensTags : allergensHierarchy;
        if (raw != null) {
            for (String tag : raw) {
                // e.g. "en:peanuts" -> "peanuts"
                if (tag.contains(":")) {
                    tag = tag.substring(tag.indexOf(":") + 1);
                }
                cleaned.add(tag.replace("-", " "));
            }
        }
        return cleaned;
    }

    public List<String> getCategoriesTags() {
        return categoriesTags != null ? categoriesTags : new ArrayList<>();
    }

    public OpenFoodFactsNutrimentsDto getNutriments() {
        return nutriments;
    }
}
