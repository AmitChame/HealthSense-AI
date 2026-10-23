package com.healthsenseai.data.repository;

import android.util.Log;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import com.healthsenseai.data.local.AppPreferences;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.RecommendationRequest;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.remote.RecommendationApiService;
import com.healthsenseai.data.remote.RetrofitClient;
import com.healthsenseai.utils.HealthRuleEngine;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Recommendation Repository providing a hybrid recommendation pipeline:
 * Integrates with remote Python Django backend, seamlessly falling back to local HealthRuleEngine.
 */
public class RecommendationRepository {

    private static final String TAG = "RecommendationRepo";

    public LiveData<Result<RecommendationResponse>> getRecommendations(FoodProduct product, List<FamilyMember> familyMembers) {
        MutableLiveData<Result<RecommendationResponse>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (product == null) {
            resultLiveData.setValue(Result.error("Product information is missing"));
            return resultLiveData;
        }

        if (familyMembers == null || familyMembers.isEmpty()) {
            resultLiveData.setValue(Result.error("Please add at least one family member to analyze health recommendations"));
            return resultLiveData;
        }

        // Check if offline mode is explicitly selected
        if (AppPreferences.getInstance().isOfflineMode()) {
            Log.d(TAG, "Offline mode active. Using local HealthRuleEngine.");
            RecommendationResponse localEval = HealthRuleEngine.evaluate(product, familyMembers);
            localEval.setSource("LOCAL_OFFLINE_MODE");
            resultLiveData.setValue(Result.success(localEval));
            return resultLiveData;
        }

        // Attempt remote Django backend call
        RecommendationRequest request = new RecommendationRequest(product, familyMembers);
        RecommendationApiService apiService = RetrofitClient.getRecommendationApiService();

        String baseUrl = AppPreferences.getInstance().getFastApiBaseUrl();
        Log.d(TAG, "PRE-FLIGHT: Sending V2 evidence request to Django. Barcode=" + product.getBarcode() + ", Members=" + familyMembers.size());
        Log.d(TAG, "TARGET_URL: " + baseUrl + "api/v2/recommend/");

        apiService.getRecommendationsV2(request).enqueue(new Callback<RecommendationResponse>() {
            @Override
            public void onResponse(Call<RecommendationResponse> call, Response<RecommendationResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    RecommendationResponse body = response.body();
                    body.setSource("REMOTE_BACKEND");
                    Log.d(TAG, "Remote analysis SUCCESS (HTTP " + response.code() + "). Source: REMOTE_BACKEND");
                    resultLiveData.setValue(Result.success(body));
                } else {
                    Log.w(TAG, "Remote analysis FAILED (HTTP " + response.code() + "). Reason: " + response.message());
                    Log.d(TAG, "Falling back to local HealthRuleEngine.");
                    RecommendationResponse fallbackEval = HealthRuleEngine.evaluate(product, familyMembers);
                    fallbackEval.setSource("LOCAL_FALLBACK_API_ERROR_" + response.code());
                    resultLiveData.setValue(Result.success(fallbackEval));
                }
            }

            @Override
            public void onFailure(Call<RecommendationResponse> call, Throwable t) {
                Log.e(TAG, "CRITICAL: Remote analysis request FAILED (Network/Protocol Error).");
                Log.e(TAG, "ERROR_MESSAGE: " + t.getMessage());
                if (t.getCause() != null) {
                    Log.e(TAG, "CAUSE: " + t.getCause().getMessage());
                }
                
                Log.d(TAG, "Falling back to local HealthRuleEngine due to connectivity failure.");
                RecommendationResponse fallbackEval = HealthRuleEngine.evaluate(product, familyMembers);
                fallbackEval.setSource("LOCAL_FALLBACK_NETWORK_ERROR");
                resultLiveData.setValue(Result.success(fallbackEval));
            }
        });

        return resultLiveData;
    }
}
