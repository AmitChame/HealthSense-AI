package com.healthsenseai.data.remote;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.healthsenseai.BuildConfig;
import com.healthsenseai.data.local.AppPreferences;
import com.healthsenseai.utils.Constants;
import java.util.concurrent.TimeUnit;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Singleton Retrofit and OkHttpClient factory for REST APIs.
 *
 * Timeout policy:
 *   - connect:  10s  (fail fast if server unreachable — triggers fallback quickly)
 *   - read:     45s  (ML inference + rule evaluation may take time on first warm-up)
 *   - write:    30s  (request payload upload)
 *   - call:     60s  (overall deadline including retries)
 *
 * Logging policy:
 *   - BODY level logging is DEBUG builds ONLY.
 *   - Release builds must NOT log authentication tokens, health data, or request/response bodies.
 */
public class RetrofitClient {

    private static final String TAG = "RetrofitClient";
    private static Retrofit foodRetrofit;
    private static FoodApiService foodApiService;

    private static Retrofit recommendationRetrofit;
    private static RecommendationApiService recommendationApiService;
    private static String currentRecommendationBaseUrl;

    private static OkHttpClient getOkHttpClient() {
        OkHttpClient.Builder builder = new OkHttpClient.Builder()
                .connectTimeout(10, TimeUnit.SECONDS)   // Fail fast on unreachable server
                .readTimeout(45, TimeUnit.SECONDS)       // Allow ML inference warm-up time
                .writeTimeout(30, TimeUnit.SECONDS)      // Request upload limit
                .callTimeout(60, TimeUnit.SECONDS);      // Absolute per-call deadline

        // SECURITY: Log request/response bodies only in debug builds.
        // Release builds must never log health data, authentication tokens, or API payloads.
        if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
            loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);
            builder.addInterceptor(loggingInterceptor);
        }

        return builder.build();
    }

    private static Gson getGson() {
        return new GsonBuilder()
                .setLenient()
                // CRITICAL: Allow NaN and Infinity serialization to prevent crashes during request building
                // if any nutritional values are un-representable as strict JSON doubles.
                .serializeSpecialFloatingPointValues()
                .create();
    }

    public static synchronized FoodApiService getFoodApiService() {
        if (foodApiService == null) {
            foodRetrofit = new Retrofit.Builder()
                    .baseUrl(Constants.OPEN_FOOD_FACTS_BASE_URL)
                    .client(getOkHttpClient())
                    .addConverterFactory(GsonConverterFactory.create(getGson()))
                    .build();
            foodApiService = foodRetrofit.create(FoodApiService.class);
        }
        return foodApiService;
    }

    public static synchronized RecommendationApiService getRecommendationApiService() {
        String configuredUrl = AppPreferences.getInstance().getFastApiBaseUrl();
        if (configuredUrl == null || configuredUrl.trim().isEmpty()) {
            configuredUrl = Constants.DEFAULT_FASTAPI_BASE_URL;
        }
        
        // Ensure URL starts with protocol and ends with slash
        if (!configuredUrl.startsWith("http")) {
            configuredUrl = "http://" + configuredUrl;
        }
        if (!configuredUrl.endsWith("/")) {
            configuredUrl += "/";
        }

        if (recommendationApiService == null || !configuredUrl.equals(currentRecommendationBaseUrl)) {
            Log.d(TAG, "Initializing Recommendation API with Base URL: " + configuredUrl);
            currentRecommendationBaseUrl = configuredUrl;
            
            try {
                recommendationRetrofit = new Retrofit.Builder()
                        .baseUrl(currentRecommendationBaseUrl)
                        .client(getOkHttpClient())
                        .addConverterFactory(GsonConverterFactory.create(getGson()))
                        .build();
                recommendationApiService = recommendationRetrofit.create(RecommendationApiService.class);
            } catch (Exception e) {
                Log.e(TAG, "Failed to build Retrofit for URL: " + currentRecommendationBaseUrl, e);
                // Fallback to absolute default if build fails
                currentRecommendationBaseUrl = Constants.DEFAULT_FASTAPI_BASE_URL;
                recommendationRetrofit = new Retrofit.Builder()
                        .baseUrl(currentRecommendationBaseUrl)
                        .client(getOkHttpClient())
                        .addConverterFactory(GsonConverterFactory.create(getGson()))
                        .build();
                recommendationApiService = recommendationRetrofit.create(RecommendationApiService.class);
            }
        }
        return recommendationApiService;
    }
}
