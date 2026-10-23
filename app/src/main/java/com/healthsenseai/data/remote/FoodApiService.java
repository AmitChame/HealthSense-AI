package com.healthsenseai.data.remote;

import com.healthsenseai.data.remote.dto.OpenFoodFactsResponse;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;

/**
 * Retrofit REST interface for packaged food product lookup.
 */
public interface FoodApiService {

    @GET("api/v0/product/{barcode}.json")
    Call<OpenFoodFactsResponse> getProductByBarcode(@Path("barcode") String barcode);
}
