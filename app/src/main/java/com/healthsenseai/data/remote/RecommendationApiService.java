package com.healthsenseai.data.remote;

import com.healthsenseai.data.model.RecommendationRequest;
import com.healthsenseai.data.model.RecommendationResponse;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

/**
 * Retrofit REST interface for communicating with the Python FastAPI AI recommendation service.
 */
public interface RecommendationApiService {

    @POST("api/analyze/")
    Call<RecommendationResponse> analyzeFoodProduct(@Body RecommendationRequest request);

    @POST("api/v1/recommend/")
    Call<RecommendationResponse> getRecommendations(@Body RecommendationRequest request);

    @POST("api/v2/recommend/")
    Call<RecommendationResponse> getRecommendationsV2(@Body RecommendationRequest request);
}
