package com.healthsenseai.data.model;

import java.io.Serializable;
import java.util.Locale;

/**
 * Standardized nutritional metrics per 100g / per serving.
 */
public class Nutriments implements Serializable {

    private Double calories;       // kcal
    private Double carbohydrates;  // grams
    private Double sugars;         // grams
    private Double proteins;       // grams
    private Double fats;           // grams
    private Double saturatedFat;   // grams
    private Double sodium;         // mg
    private Double fiber;          // grams
    private Double salt;           // grams

    public Nutriments() {
    }

    public Double getCalories() {
        return calories;
    }

    public void setCalories(Double calories) {
        this.calories = calories;
    }

    public Double getCarbohydrates() {
        return carbohydrates;
    }

    public void setCarbohydrates(Double carbohydrates) {
        this.carbohydrates = carbohydrates;
    }

    public Double getSugars() {
        return sugars;
    }

    public void setSugars(Double sugars) {
        this.sugars = sugars;
    }

    public Double getProteins() {
        return proteins;
    }

    public void setProteins(Double proteins) {
        this.proteins = proteins;
    }

    public Double getFats() {
        return fats;
    }

    public void setFats(Double fats) {
        this.fats = fats;
    }

    public Double getSaturatedFat() {
        return saturatedFat;
    }

    public void setSaturatedFat(Double saturatedFat) {
        this.saturatedFat = saturatedFat;
    }

    public Double getSodium() {
        return sodium;
    }

    public void setSodium(Double sodium) {
        this.sodium = sodium;
    }

    public Double getFiber() {
        return fiber;
    }

    public void setFiber(Double fiber) {
        this.fiber = fiber;
    }

    public Double getSalt() {
        return salt;
    }

    public void setSalt(Double salt) {
        this.salt = salt;
    }

    public String getFormattedCalories() {
        return calories != null ? String.format(Locale.getDefault(), "%.0f kcal", calories) : "Not available";
    }

    public String getFormattedSugars() {
        return sugars != null ? String.format(Locale.getDefault(), "%.1f g", sugars) : "Not available";
    }

    public String getFormattedSodium() {
        return sodium != null ? String.format(Locale.getDefault(), "%.0f mg", sodium) : "Not available";
    }

    public String getFormattedFats() {
        return fats != null ? String.format(Locale.getDefault(), "%.1f g", fats) : "Not available";
    }

    public String getFormattedSaturatedFat() {
        return saturatedFat != null ? String.format(Locale.getDefault(), "%.1f g", saturatedFat) : "Not available";
    }

    public String getFormattedProteins() {
        return proteins != null ? String.format(Locale.getDefault(), "%.1f g", proteins) : "Not available";
    }

    public String getFormattedCarbohydrates() {
        return carbohydrates != null ? String.format(Locale.getDefault(), "%.1f g", carbohydrates) : "Not available";
    }

    public String getFormattedFiber() {
        return fiber != null ? String.format(Locale.getDefault(), "%.1f g", fiber) : "Not available";
    }
}
