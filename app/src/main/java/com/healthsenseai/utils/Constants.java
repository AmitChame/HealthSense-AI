package com.healthsenseai.utils;

/**
 * Global Constants for HealthSense AI.
 */
public final class Constants {

    private Constants() {
        // Prevent instantiation
    }

    // Firestore Collection Names
    public static final String COLLECTION_USERS = "users";
    public static final String COLLECTION_FAMILY_MEMBERS = "familyMembers";
    public static final String COLLECTION_SCAN_HISTORY = "scanHistory";

    // Intent Extra Keys
    public static final String EXTRA_BARCODE = "extra_barcode";
    public static final String EXTRA_FOOD_PRODUCT = "extra_food_product";
    public static final String EXTRA_FAMILY_MEMBER = "extra_family_member";
    public static final String EXTRA_FAMILY_MEMBER_ID = "extra_family_member_id";
    public static final String EXTRA_RECOMMENDATION_RESPONSE = "extra_recommendation_response";
    public static final String EXTRA_HISTORY_ITEM = "extra_history_item";

    // Shared Preferences Keys
    public static final String PREF_NAME = "healthsense_ai_prefs";
    public static final String KEY_FASTAPI_URL = "pref_fastapi_backend_url";
    public static final String KEY_OFFLINE_MODE = "pref_offline_mode";

    // Default API Endpoints
    public static final String OPEN_FOOD_FACTS_BASE_URL = "https://world.openfoodfacts.org/";
    public static final String DEFAULT_FASTAPI_BASE_URL = "http://10.0.2.2:8000/"; // Standard Android Emulator localhost

    // Standard Nutritional Reference Thresholds (Per 100g)
    // High sugar > 10g, High sodium > 400mg (0.4g), High saturated fat > 4g
    public static final double THRESHOLD_HIGH_SUGAR_100G = 10.0;
    public static final double THRESHOLD_DIABETIC_SUGAR_MAX_100G = 5.0;
    public static final double THRESHOLD_HIGH_SODIUM_MG_100G = 400.0;
    public static final double THRESHOLD_HYPERTENSION_SODIUM_MG_100G = 250.0;
    public static final double THRESHOLD_HIGH_SAT_FAT_100G = 4.0;
    public static final double THRESHOLD_CHOLESTEROL_SAT_FAT_100G = 2.0;

    // Disclaimer Message
    public static final String MEDICAL_DISCLAIMER =
            "This application provides informational food-health decision support and is not a substitute for professional medical advice, clinical diagnosis, or treatment.";
}
