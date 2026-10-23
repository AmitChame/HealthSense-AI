package com.healthsenseai;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FamilyRecommendation;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.Nutriments;
import com.healthsenseai.data.model.RecommendationCategory;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.data.model.RiskLevel;
import com.healthsenseai.utils.HealthRuleEngine;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.junit.Before;
import org.junit.Test;

/**
 * Unit tests for HealthRuleEngine deterministic dietary and allergen analysis.
 */
public class HealthRuleEngineTest {

    private FamilyMember diabeticMember;
    private FamilyMember peanutAllergicMember;
    private FamilyMember healthyMember;

    @Before
    public void setUp() {
        diabeticMember = new FamilyMember("John", 45, "Male");
        diabeticMember.setId("member_1");
        diabeticMember.setHealthConditions(Collections.singletonList("Diabetes (Type 2)"));

        peanutAllergicMember = new FamilyMember("Sarah", 12, "Female");
        peanutAllergicMember.setId("member_2");
        peanutAllergicMember.setAllergies(Collections.singletonList("Peanuts"));

        healthyMember = new FamilyMember("Alex", 25, "Other");
        healthyMember.setId("member_3");
        healthyMember.setHealthConditions(Collections.singletonList("None"));
    }

    @Test
    public void testHighSugarProduct_forDiabeticMember_returnsNotRecommended() {
        FoodProduct sugaryCereal = new FoodProduct("123456", "Sugary Frosted Flakes", "Brand A");
        Nutriments nutriments = new Nutriments();
        nutriments.setSugars(25.0); // 25g sugar / 100g -> high sugar
        sugaryCereal.setNutriments(nutriments);

        FamilyRecommendation rec = HealthRuleEngine.evaluateMember(sugaryCereal, diabeticMember);

        assertNotNull(rec);
        assertEquals(RecommendationCategory.NOT_RECOMMENDED, rec.getCategory());
        assertEquals(RiskLevel.HIGH, rec.getRiskLevel());
        assertTrue(rec.getRiskScore() >= 70);
    }

    @Test
    public void testPeanutAllergy_whenProductContainsPeanuts_returnsNotRecommended() {
        FoodProduct peanutButter = new FoodProduct("789012", "Peanut Butter Spread", "Brand B");
        peanutButter.setAllergens(Collections.singletonList("peanuts"));
        peanutButter.setIngredients("Roasted peanuts, salt, hydrogenated vegetable oil");

        FamilyRecommendation rec = HealthRuleEngine.evaluateMember(peanutButter, peanutAllergicMember);

        assertNotNull(rec);
        assertEquals(RecommendationCategory.NOT_RECOMMENDED, rec.getCategory());
        assertEquals(RiskLevel.HIGH, rec.getRiskLevel());
        assertTrue(rec.getWarnings().size() > 0);
    }

    @Test
    public void testLowSugarLowSodiumProduct_forHealthyMember_returnsSuitable() {
        FoodProduct oats = new FoodProduct("345678", "Rolled Oats", "Brand C");
        Nutriments nutriments = new Nutriments();
        nutriments.setSugars(1.0);
        nutriments.setSodium(5.0);
        nutriments.setSaturatedFat(0.5);
        nutriments.setCalories(150.0);
        oats.setNutriments(nutriments);

        FamilyRecommendation rec = HealthRuleEngine.evaluateMember(oats, healthyMember);

        assertNotNull(rec);
        assertEquals(RecommendationCategory.SUITABLE, rec.getCategory());
        assertEquals(RiskLevel.LOW, rec.getRiskLevel());
    }

    @Test
    public void testFamilyEvaluationSummary() {
        FoodProduct cookie = new FoodProduct("999999", "Choco Peanut Cookie", "Brand D");
        cookie.setAllergens(Collections.singletonList("peanuts"));
        Nutriments nutriments = new Nutriments();
        nutriments.setSugars(22.0);
        cookie.setNutriments(nutriments);

        List<FamilyMember> family = new ArrayList<>();
        family.add(diabeticMember);
        family.add(peanutAllergicMember);
        family.add(healthyMember);

        RecommendationResponse response = HealthRuleEngine.evaluate(cookie, family);

        assertNotNull(response);
        assertEquals(3, response.getRecommendations().size());
        String verdict = response.getOverallVerdict().toLowerCase();
        assertTrue(verdict.contains("considerations") || verdict.contains("conflicts") || verdict.contains("caution"));
    }
}
