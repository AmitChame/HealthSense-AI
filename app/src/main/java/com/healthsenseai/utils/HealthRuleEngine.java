package com.healthsenseai.utils;

import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FamilyRecommendation;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.HealthFactor;
import com.healthsenseai.data.model.Nutriments;
import com.healthsenseai.data.model.RecommendationCategory;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.data.model.RiskLevel;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * HealthRuleEngine — Client-side deterministic nutritional analysis and health decision support engine.
 * Evaluates packaged food products against family member health conditions, dietary preferences, and allergies.
 */
public final class HealthRuleEngine {

    private HealthRuleEngine() {
        // Prevent instantiation
    }

    public static RecommendationResponse evaluate(FoodProduct product, List<FamilyMember> familyMembers) {
        if (product == null) {
            RecommendationResponse empty = new RecommendationResponse("", "Unknown Product", new ArrayList<>());
            empty.setSource("LOCAL_FALLBACK");
            empty.setAssessmentConfidence("LOW");
            empty.setFrequencyRecommendation("OCCASIONAL");
            return empty;
        }

        String grade = calculateProductGrade(product);
        String generalFrequency = calculateGeneralFrequency(grade, product);
        String confidence = calculateConfidence(product);

        List<FamilyRecommendation> recommendations = new ArrayList<>();
        if (familyMembers != null) {
            for (FamilyMember member : familyMembers) {
                FamilyRecommendation rec = evaluateMember(product, member);
                rec.setFoodGrade(grade);
                rec.setAssessmentConfidence(confidence);
                recommendations.add(rec);
            }
        }

        RecommendationResponse response = new RecommendationResponse(
                product.getBarcode(),
                product.getProductName(),
                recommendations
        );

        response.setFoodGrade(grade);
        response.setSource("LOCAL_FALLBACK");
        response.setActiveModel("Offline Analysis — Limited Evidence");
        response.setAssessmentConfidence(confidence);
        response.setFrequencyRecommendation(generalFrequency);

        // Overall summary verdict
        boolean hasNotRecommended = false;
        boolean hasCaution = false;
        for (FamilyRecommendation rec : recommendations) {
            if (rec.getCategory() == RecommendationCategory.NOT_RECOMMENDED) {
                hasNotRecommended = true;
            } else if (rec.getCategory() == RecommendationCategory.CAUTION) {
                hasCaution = true;
            }
        }

        if (hasNotRecommended) {
            response.setOverallVerdict(String.format("Profile %s — Significant dietary considerations or allergen conflicts identified for one or more profiles. Review individual warnings.", grade));
        } else if (hasCaution) {
            response.setOverallVerdict(String.format("Profile %s — Specific nutritional considerations identified. Portion awareness and moderation advised.", grade));
        } else {
            response.setOverallVerdict(String.format("Profile %s — Favorable profile based on available offline label data. Review individual member considerations.", grade));
        }

        return response;
    }

    public static FamilyRecommendation evaluateMember(FoodProduct product, FamilyMember member) {
        FamilyRecommendation rec = new FamilyRecommendation();
        rec.setFamilyMemberId(member.getId());
        rec.setFamilyMemberName(member.getName());
        rec.setFamilyMemberAge(member.getAge());

        // Build health summary text
        StringBuilder healthSummary = new StringBuilder();
        if (member.getHealthConditions() != null && !member.getHealthConditions().isEmpty()) {
            healthSummary.append(String.join(", ", member.getHealthConditions()));
        }
        if (member.getAllergies() != null && !member.getAllergies().isEmpty()) {
            if (healthSummary.length() > 0) healthSummary.append(" | Allergies: ");
            healthSummary.append(String.join(", ", member.getAllergies()));
        }
        if (member.getDietaryPreferences() != null && !member.getDietaryPreferences().isEmpty()) {
            if (healthSummary.length() > 0) healthSummary.append(" | Diet: ");
            healthSummary.append(String.join(", ", member.getDietaryPreferences()));
        }
        rec.setHealthSummary(healthSummary.toString());

        List<HealthFactor> factors = new ArrayList<>();
        List<String> warnings = new ArrayList<>();

        Nutriments nutriments = product.getNutriments() != null ? product.getNutriments() : new Nutriments();
        Double sugars = nutriments.getSugars();
        Double sodium = nutriments.getSodium();
        Double satFat = nutriments.getSaturatedFat();
        Double calories = nutriments.getCalories();
        String ingredientsLower = product.getIngredients() != null ? product.getIngredients().toLowerCase(Locale.ROOT) : "";
        List<String> productAllergens = product.getAllergens();

        boolean isSevereRisk = false;
        boolean isModerateRisk = false;
        int riskScore = 0;

        // 1. Check Allergies (Immediate NOT RECOMMENDED - Deterministic Override)
        if (member.getAllergies() != null) {
            for (String allergy : member.getAllergies()) {
                if (allergy == null || allergy.equalsIgnoreCase("None") || allergy.trim().isEmpty()) continue;
                String allergyLower = allergy.toLowerCase(Locale.ROOT).trim();

                boolean matchedAllergen = false;
                if (productAllergens != null) {
                    for (String pa : productAllergens) {
                        if (pa.toLowerCase(Locale.ROOT).contains(allergyLower)) {
                            matchedAllergen = true;
                            break;
                        }
                    }
                }

                if (!matchedAllergen && ingredientsLower.contains(allergyLower)) {
                    matchedAllergen = true;
                }

                if (matchedAllergen) {
                    isSevereRisk = true;
                    riskScore += 80;
                    factors.add(new HealthFactor(
                            "Allergen Alert: " + allergy,
                            RiskLevel.HIGH,
                            "Contains or traces of " + allergy + ", which triggers your recorded allergy.",
                            true,
                            allergy,
                            "0 tolerance"
                    ));
                    warnings.add("Contains Allergen: " + allergy);
                }
            }
        }

        // 2. Age-Aware Child Safety Rules
        int age = member.getAge();
        if (age < 12) {
            boolean isCaffeine = ingredientsLower.contains("caffeine") || ingredientsLower.contains("energy drink") ||
                    ingredientsLower.contains("taurine") || ingredientsLower.contains("guarana");
            if (isCaffeine) {
                isSevereRisk = true;
                riskScore += 70;
                factors.add(new HealthFactor(
                        "Child Safety: High Caffeine / Stimulant",
                        RiskLevel.HIGH,
                        String.format(Locale.getDefault(), "Contains caffeine or stimulants unsuitable for children (Age %d).", age),
                        true,
                        "Caffeine / Stimulants",
                        "Avoid for children < 12"
                ));
                warnings.add("Not recommended for children under 12 due to caffeine/stimulants.");
            }

            boolean hasArtificialColors = ingredientsLower.contains("tartrazine") || ingredientsLower.contains("allura red") ||
                    ingredientsLower.contains("sunset yellow") || ingredientsLower.contains("e102") ||
                    ingredientsLower.contains("e129") || ingredientsLower.contains("e110");
            if (hasArtificialColors) {
                isModerateRisk = true;
                riskScore += 25;
                factors.add(new HealthFactor(
                        "Child Caution: Artificial Colorings",
                        RiskLevel.MODERATE,
                        String.format(Locale.getDefault(), "Contains artificial food dyes warranting portion caution for children (Age %d).", age)
                ));
            }

            if (age < 5) {
                if (sugars != null && sugars > 20.0) {
                    isModerateRisk = true;
                    riskScore += 25;
                    factors.add(new HealthFactor(
                            "Child Caution: High Sugar",
                            RiskLevel.MODERATE,
                            String.format(Locale.getDefault(), "Sugar level (%.1fg/100g) exceeds pediatric guidelines for young children (Age %d).", sugars, age)
                    ));
                }
                if (sodium != null && sodium > 400.0) {
                    isModerateRisk = true;
                    riskScore += 25;
                    factors.add(new HealthFactor(
                            "Child Caution: High Sodium",
                            RiskLevel.MODERATE,
                            String.format(Locale.getDefault(), "Sodium level (%.0fmg/100g) exceeds pediatric thresholds for young children (Age %d).", sodium, age)
                    ));
                }
            }
        }

        // 3. Dietary Preferences (Vegetarian, Vegan)
        if (member.getDietaryPreferences() != null) {
            for (String diet : member.getDietaryPreferences()) {
                if (diet == null) continue;
                String dietLower = diet.toLowerCase(Locale.ROOT);

                if (dietLower.contains("vegetarian")) {
                    boolean hasMeat = ingredientsLower.contains("gelatin") || ingredientsLower.contains("carmine") ||
                            ingredientsLower.contains("lard") || ingredientsLower.contains("chicken") ||
                            ingredientsLower.contains("beef") || ingredientsLower.contains("pork") ||
                            ingredientsLower.contains("fish") || ingredientsLower.contains("meat");
                    if (hasMeat) {
                        isSevereRisk = true;
                        riskScore += 45;
                        factors.add(new HealthFactor(
                                "Dietary Conflict: Non-Vegetarian",
                                RiskLevel.HIGH,
                                "Contains animal or meat-derived ingredients incompatible with Vegetarian preference.",
                                true,
                                "Animal derivative present",
                                "Vegetarian required"
                        ));
                        warnings.add("Contains non-vegetarian ingredients (e.g. meat, gelatin, or carmine).");
                    }
                }

                if (dietLower.contains("vegan")) {
                    boolean hasAnimal = ingredientsLower.contains("milk") || ingredientsLower.contains("egg") ||
                            ingredientsLower.contains("honey") || ingredientsLower.contains("whey") ||
                            ingredientsLower.contains("casein") || ingredientsLower.contains("butter") ||
                            ingredientsLower.contains("cheese") || ingredientsLower.contains("gelatin");
                    if (hasAnimal) {
                        isSevereRisk = true;
                        riskScore += 45;
                        factors.add(new HealthFactor(
                                "Dietary Conflict: Non-Vegan",
                                RiskLevel.HIGH,
                                "Contains dairy, egg, or animal-derived ingredients incompatible with Vegan preference.",
                                true,
                                "Animal derivative present",
                                "Vegan required"
                        ));
                        warnings.add("Contains animal or dairy ingredients incompatible with a vegan diet.");
                    }
                }
            }
        }

        // 4. Check Health Conditions
        if (member.getHealthConditions() != null) {
            for (String condition : member.getHealthConditions()) {
                if (condition == null || condition.equalsIgnoreCase("None")) continue;
                String condLower = condition.toLowerCase(Locale.ROOT);

                // Diabetes evaluation
                if (condLower.contains("diabet")) {
                    if (sugars != null) {
                        if (sugars >= Constants.THRESHOLD_HIGH_SUGAR_100G) {
                            isSevereRisk = true;
                            riskScore += 45;
                            factors.add(new HealthFactor(
                                     "High Sugar for Diabetes",
                                    RiskLevel.HIGH,
                                    String.format(Locale.getDefault(), "Sugar level (%.1fg/100g) significantly exceeds recommended diabetic threshold (%.1fg).", sugars, Constants.THRESHOLD_DIABETIC_SUGAR_MAX_100G),
                                    false,
                                    String.format(Locale.getDefault(), "%.1fg", sugars),
                                    String.format(Locale.getDefault(), "<%.1fg", Constants.THRESHOLD_DIABETIC_SUGAR_MAX_100G)
                            ));
                        } else if (sugars >= Constants.THRESHOLD_DIABETIC_SUGAR_MAX_100G) {
                            isModerateRisk = true;
                            riskScore += 25;
                            factors.add(new HealthFactor(
                                    "Moderate Sugar Content",
                                    RiskLevel.MODERATE,
                                    String.format(Locale.getDefault(), "Sugar level (%.1fg/100g) requires strict portion control for diabetes management.", sugars),
                                    false,
                                    String.format(Locale.getDefault(), "%.1fg", sugars),
                                    String.format(Locale.getDefault(), "<%.1fg", Constants.THRESHOLD_DIABETIC_SUGAR_MAX_100G)
                            ));
                        }
                    }
                    if (ingredientsLower.contains("high fructose corn syrup") || ingredientsLower.contains("maltodextrin") || ingredientsLower.contains("corn syrup")) {
                        isModerateRisk = true;
                        riskScore += 15;
                        factors.add(new HealthFactor(
                                "High Glycemic Additives",
                                RiskLevel.MODERATE,
                                "Contains refined high-glycemic sweeteners that cause rapid blood glucose spikes."
                        ));
                    }
                }

                // Hypertension / High Blood Pressure
                if (condLower.contains("hypertens") || condLower.contains("blood pressure")) {
                    if (sodium != null) {
                        if (sodium >= Constants.THRESHOLD_HIGH_SODIUM_MG_100G) {
                            isSevereRisk = true;
                            riskScore += 45;
                            factors.add(new HealthFactor(
                                    "High Sodium Level",
                                    RiskLevel.HIGH,
                                    String.format(Locale.getDefault(), "Sodium content (%.0fmg/100g) exceeds safety limits for hypertension management (%.0fmg).", sodium, Constants.THRESHOLD_HYPERTENSION_SODIUM_MG_100G),
                                    false,
                                    String.format(Locale.getDefault(), "%.0fmg", sodium),
                                    String.format(Locale.getDefault(), "<%.0fmg", Constants.THRESHOLD_HYPERTENSION_SODIUM_MG_100G)
                            ));
                        } else if (sodium >= Constants.THRESHOLD_HYPERTENSION_SODIUM_MG_100G) {
                            isModerateRisk = true;
                            riskScore += 20;
                            factors.add(new HealthFactor(
                                    "Moderate Sodium",
                                    RiskLevel.MODERATE,
                                    String.format(Locale.getDefault(), "Sodium content (%.0fmg/100g) should be monitored for blood pressure control.", sodium),
                                    false,
                                    String.format(Locale.getDefault(), "%.0fmg", sodium),
                                    String.format(Locale.getDefault(), "<%.0fmg", Constants.THRESHOLD_HYPERTENSION_SODIUM_MG_100G)
                            ));
                        }
                    }
                }

                // High Cholesterol / Heart Health
                if (condLower.contains("cholesterol") || condLower.contains("heart") || condLower.contains("hyperlipidemia")) {
                    if (satFat != null) {
                        if (satFat >= Constants.THRESHOLD_HIGH_SAT_FAT_100G) {
                            isSevereRisk = true;
                            riskScore += 40;
                            factors.add(new HealthFactor(
                                    "High Saturated Fat",
                                    RiskLevel.HIGH,
                                    String.format(Locale.getDefault(), "Saturated fat (%.1fg/100g) exceeds recommended heart-health ceiling (%.1fg).", satFat, Constants.THRESHOLD_CHOLESTEROL_SAT_FAT_100G),
                                    false,
                                    String.format(Locale.getDefault(), "%.1fg", satFat),
                                    String.format(Locale.getDefault(), "<%.1fg", Constants.THRESHOLD_CHOLESTEROL_SAT_FAT_100G)
                            ));
                        } else if (satFat >= Constants.THRESHOLD_CHOLESTEROL_SAT_FAT_100G) {
                            isModerateRisk = true;
                            riskScore += 20;
                            factors.add(new HealthFactor(
                                    "Elevated Saturated Fat",
                                    RiskLevel.MODERATE,
                                    String.format(Locale.getDefault(), "Saturated fat (%.1fg/100g) should be limited for optimal lipid profiles.", satFat),
                                    false,
                                    String.format(Locale.getDefault(), "%.1fg", satFat),
                                    String.format(Locale.getDefault(), "<%.1fg", Constants.THRESHOLD_CHOLESTEROL_SAT_FAT_100G)
                            ));
                        }
                    }
                    if (ingredientsLower.contains("hydrogenated") || ingredientsLower.contains("palm oil") || ingredientsLower.contains("trans fat")) {
                        isModerateRisk = true;
                        riskScore += 15;
                        factors.add(new HealthFactor(
                                "Unfavorable Lipids",
                                RiskLevel.MODERATE,
                                "Contains processed oils with elevated atherogenic potential."
                        ));
                    }
                }

                // Celiac / Gluten Intolerance
                if (condLower.contains("celiac") || condLower.contains("gluten")) {
                    if (ingredientsLower.contains("wheat") || ingredientsLower.contains("barley") || ingredientsLower.contains("rye") || ingredientsLower.contains("gluten")) {
                        isSevereRisk = true;
                        riskScore += 80;
                        factors.add(new HealthFactor(
                                "Contains Gluten",
                                RiskLevel.HIGH,
                                "Product contains wheat or gluten-derived grains unsuitable for Celiac condition.",
                                true,
                                "Gluten present",
                                "Gluten-free required"
                        ));
                    }
                }

                // Lactose Intolerance
                if (condLower.contains("lactose") || condLower.contains("dairy")) {
                    if (ingredientsLower.contains("milk") || ingredientsLower.contains("lactose") || ingredientsLower.contains("whey") || ingredientsLower.contains("casein")) {
                        isModerateRisk = true;
                        riskScore += 35;
                        factors.add(new HealthFactor(
                                "Contains Dairy / Lactose",
                                RiskLevel.MODERATE,
                                "Contains dairy components that may cause gastrointestinal distress for lactose intolerance."
                        ));
                    }
                }

                // Kidney Disease / Renal Diet Special Rule (KDIGO 2020)
                if (condLower.contains("kidney") || condLower.contains("renal") || condLower.contains("ckd") || condLower.contains("nephro")) {
                    isModerateRisk = true;
                    riskScore += 30;
                    factors.add(new HealthFactor(
                            "Renal Diet Clinical Uncertainty",
                            RiskLevel.MODERATE,
                            "Packaging labels lack critical clinical parameters (potassium, bioavailable phosphorus). Clinical renal dietitian guidance required."
                    ));
                    warnings.add("Renal-diet suitability cannot be determined reliably from packaging label alone. Consult a specialized renal clinician.");
                }
            }
        }

        // 5. Finalize Category, Risk Level, Frequency & Reason
        String memberFrequency;
        if (isSevereRisk) {
            rec.setCategory(RecommendationCategory.NOT_RECOMMENDED);
            rec.setRiskLevel(RiskLevel.HIGH);
            rec.setRiskScore(Math.min(100, Math.max(70, riskScore)));
            rec.setSummaryReason("Significant nutritional considerations, child safety alerts, or allergen conflicts identified for " + member.getName() + "'s health profile.");
            memberFrequency = "AVOID";
        } else if (isModerateRisk) {
            rec.setCategory(RecommendationCategory.CAUTION);
            rec.setRiskLevel(RiskLevel.MODERATE);
            rec.setRiskScore(Math.min(69, Math.max(30, riskScore)));
            rec.setSummaryReason("Contains sensitive nutrients (e.g. sugar, sodium, or saturated fat) that warrant portion mindfulness for " + member.getName() + ".");
            memberFrequency = "OCCASIONAL";
        } else {
            rec.setCategory(RecommendationCategory.SUITABLE);
            rec.setRiskLevel(RiskLevel.LOW);
            rec.setRiskScore(Math.max(5, riskScore));
            rec.setSummaryReason("Nutrient levels align favorably with general population dietary references for " + member.getName() + "'s recorded profile with no detected allergen conflicts.");
            memberFrequency = "REGULAR";
            factors.add(new HealthFactor(
                    "Nutritional Balance",
                    RiskLevel.LOW,
                    "Nutrient profile aligns favorably with general dietary references."
            ));
        }

        rec.setFrequencyRecommendation(memberFrequency);
        rec.setModelName("Offline Analysis — Limited Evidence");
        rec.setConfidence(0.85);
        rec.setHealthFactors(factors);
        rec.setWarnings(warnings);
        return rec;
    }

    private static String calculateProductGrade(FoodProduct product) {
        Nutriments n = product.getNutriments() != null ? product.getNutriments() : new Nutriments();
        Double sugars = n.getSugars();
        Double sodium = n.getSodium();
        Double satFat = n.getSaturatedFat();

        int penalty = 0;
        if (sugars != null) {
            if (sugars > 22.5) penalty += 35;
            else if (sugars > 10.0) penalty += 15;
        }
        if (sodium != null) {
            if (sodium > 600.0) penalty += 35;
            else if (sodium > 300.0) penalty += 15;
        }
        if (satFat != null) {
            if (satFat > 5.0) penalty += 30;
            else if (satFat > 2.5) penalty += 10;
        }

        int score = Math.max(0, 100 - penalty);
        if (score >= 80) return "A";
        if (score >= 65) return "B";
        if (score >= 50) return "C";
        if (score >= 35) return "D";
        return "E";
    }

    private static String calculateGeneralFrequency(String grade, FoodProduct product) {
        switch (grade) {
            case "A":
            case "B":
                return "REGULAR";
            case "C":
                return "OCCASIONAL";
            case "D":
            case "E":
                return "LIMIT FREQUENCY";
            default:
                return "OCCASIONAL";
        }
    }

    private static String calculateConfidence(FoodProduct product) {
        Nutriments n = product.getNutriments();
        if (n == null) return "LOW";
        int count = 0;
        if (n.getCalories() != null) count++;
        if (n.getSugars() != null) count++;
        if (n.getSodium() != null) count++;
        if (n.getSaturatedFat() != null) count++;
        if (n.getProteins() != null) count++;

        if (count >= 4 && product.getIngredients() != null && !product.getIngredients().isEmpty()) {
            return "HIGH";
        } else if (count >= 2) {
            return "MEDIUM";
        }
        return "LOW";
    }
}
