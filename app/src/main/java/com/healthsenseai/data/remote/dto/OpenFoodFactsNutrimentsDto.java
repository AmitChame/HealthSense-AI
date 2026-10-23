package com.healthsenseai.data.remote.dto;

import com.google.gson.JsonElement;
import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

/**
 * DTO mapping OpenFoodFacts 'nutriments' JSON object.
 * Supports multiple naming conventions (hyphen vs underscore, 100g vs serving, kcal vs kJ)
 * and handles non-numeric strings (e.g. "< 0.1").
 */
public class OpenFoodFactsNutrimentsDto implements Serializable {

    // --- Calories / Energy ---
    @SerializedName("energy-kcal_100g")
    private JsonElement energyKcal100g;

    @SerializedName("energy-kcal_serving")
    private JsonElement energyKcalServing;

    @SerializedName("energy_kcal_100g")
    private JsonElement energyKcal100gUnderscore;

    @SerializedName("energy_kcal_serving")
    private JsonElement energyKcalServingUnderscore;

    @SerializedName("energy-kj_100g")
    private JsonElement energyKj100g;

    @SerializedName("energy-kj_serving")
    private JsonElement energyKjServing;

    @SerializedName("energy_kj_100g")
    private JsonElement energyKj100gUnderscore;

    @SerializedName("energy_kj_serving")
    private JsonElement energyKjServingUnderscore;

    @SerializedName("energy-kcal")
    private JsonElement energyKcal;

    // --- Sugars ---
    @SerializedName("sugars_100g")
    private JsonElement sugars100g;

    @SerializedName("sugars_serving")
    private JsonElement sugarsServing;

    @SerializedName("sugars")
    private JsonElement sugars;

    // --- Sodium & Salt ---
    @SerializedName("sodium_100g")
    private JsonElement sodium100g;

    @SerializedName("sodium_serving")
    private JsonElement sodiumServing;

    @SerializedName("sodium")
    private JsonElement sodium;

    @SerializedName("salt_100g")
    private JsonElement salt100g;

    @SerializedName("salt_serving")
    private JsonElement saltServing;

    // --- Fats ---
    @SerializedName("fat_100g")
    private JsonElement fat100g;

    @SerializedName("fat_serving")
    private JsonElement fatServing;

    @SerializedName("fat")
    private JsonElement fat;

    // --- Saturated Fat ---
    @SerializedName("saturated-fat_100g")
    private JsonElement saturatedFat100g;

    @SerializedName("saturated-fat_serving")
    private JsonElement saturatedFatServing;

    @SerializedName("saturated_fat_100g")
    private JsonElement saturatedFat100gUnderscore;

    @SerializedName("saturated_fat_serving")
    private JsonElement saturatedFatServingUnderscore;

    @SerializedName("saturated-fat")
    private JsonElement saturatedFat;

    // --- Proteins ---
    @SerializedName("proteins_100g")
    private JsonElement proteins100g;

    @SerializedName("proteins_serving")
    private JsonElement proteinsServing;

    @SerializedName("proteins")
    private JsonElement proteins;

    // --- Carbohydrates ---
    @SerializedName("carbohydrates_100g")
    private JsonElement carbohydrates100g;

    @SerializedName("carbohydrates_serving")
    private JsonElement carbohydratesServing;

    @SerializedName("carbohydrates")
    private JsonElement carbohydrates;

    // --- Fiber ---
    @SerializedName("fiber_100g")
    private JsonElement fiber100g;

    @SerializedName("fiber_serving")
    private JsonElement fiberServing;

    @SerializedName("fiber")
    private JsonElement fiber;

    public Double getCalories() {
        Double val = firstNonNull(energyKcal100g, energyKcal100gUnderscore, energyKcalServing, energyKcalServingUnderscore, energyKcal);
        if (val != null) return val;

        // Try kJ fallback (1 kcal = 4.184 kJ)
        Double kjVal = firstNonNull(energyKj100g, energyKj100gUnderscore, energyKjServing, energyKjServingUnderscore);
        if (kjVal != null) return kjVal / 4.184;

        return null;
    }

    public Double getSugars() {
        return firstNonNull(sugars100g, sugarsServing, sugars);
    }

    public Double getSodiumMg() {
        Double sodiumVal = firstNonNull(sodium100g, sodiumServing, sodium);
        if (sodiumVal != null) {
            // OpenFoodFacts usually returns sodium in grams, convert to mg
            return sodiumVal * 1000.0;
        }

        // Try salt fallback (sodium = salt / 2.5)
        Double saltVal = firstNonNull(salt100g, saltServing);
        if (saltVal != null) {
            return (saltVal / 2.5) * 1000.0;
        }

        return null;
    }

    public Double getFats() {
        return firstNonNull(fat100g, fatServing, fat);
    }

    public Double getSaturatedFat() {
        return firstNonNull(saturatedFat100g, saturatedFat100gUnderscore, saturatedFatServing, saturatedFatServingUnderscore, saturatedFat);
    }

    public Double getProteins() {
        return firstNonNull(proteins100g, proteinsServing, proteins);
    }

    public Double getCarbohydrates() {
        return firstNonNull(carbohydrates100g, carbohydratesServing, carbohydrates);
    }

    public Double getFiber() {
        return firstNonNull(fiber100g, fiberServing, fiber);
    }

    public Double getSalt() {
        return firstNonNull(salt100g, saltServing);
    }

    private Double firstNonNull(JsonElement... elements) {
        for (JsonElement element : elements) {
            Double val = parseDouble(element);
            if (val != null) return val;
        }
        return null;
    }

    private Double parseDouble(JsonElement element) {
        if (element == null || element.isJsonNull()) return null;
        try {
            if (element.isJsonPrimitive()) {
                if (element.getAsJsonPrimitive().isNumber()) {
                    return element.getAsDouble();
                } else if (element.getAsJsonPrimitive().isString()) {
                    String s = element.getAsString().replaceAll("[^0-9.]", "");
                    if (!s.isEmpty()) {
                        return Double.parseDouble(s);
                    }
                }
            }
        } catch (Exception e) {
            // Ignore parse errors
        }
        return null;
    }
}
