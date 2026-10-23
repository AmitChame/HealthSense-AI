package com.healthsenseai.data.repository;

import android.util.Log;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.Nutriments;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.remote.FoodApiService;
import com.healthsenseai.data.remote.RetrofitClient;
import com.healthsenseai.data.remote.dto.OpenFoodFactsNutrimentsDto;
import com.healthsenseai.data.remote.dto.OpenFoodFactsProductDto;
import com.healthsenseai.data.remote.dto.OpenFoodFactsResponse;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Repository for fetching packaged food product information by barcode from REST API.
 */
public class FoodProductRepository {

    private static final String TAG = "FoodProductRepository";
    private final FoodApiService foodApiService;

    public FoodProductRepository() {
        this.foodApiService = RetrofitClient.getFoodApiService();
    }

    public LiveData<Result<FoodProduct>> getProductByBarcode(String barcode) {
        MutableLiveData<Result<FoodProduct>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (barcode == null || barcode.trim().isEmpty()) {
            resultLiveData.setValue(Result.error("Invalid barcode"));
            return resultLiveData;
        }

        foodApiService.getProductByBarcode(barcode.trim()).enqueue(new Callback<OpenFoodFactsResponse>() {
            @Override
            public void onResponse(Call<OpenFoodFactsResponse> call, Response<OpenFoodFactsResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    OpenFoodFactsResponse offResponse = response.body();
                    Log.d(TAG, "API Response for " + barcode + ": " + (offResponse.isFound() ? "Found" : "Not Found"));
                    if (offResponse.isFound() && offResponse.getProduct() != null) {
                        OpenFoodFactsProductDto productDto = offResponse.getProduct();
                        if (productDto.getNutriments() == null) {
                            Log.w(TAG, "Nutriments DTO is NULL for barcode: " + barcode);
                        } else {
                            Log.d(TAG, "Nutriments found for " + barcode);
                        }
                        FoodProduct domainProduct = mapDtoToDomain(productDto, barcode);
                        resultLiveData.setValue(Result.success(domainProduct));
                    } else {
                        resultLiveData.setValue(Result.error("Product with barcode '" + barcode + "' was not found in the food database."));
                    }
                } else {
                    resultLiveData.setValue(Result.error("Server error retrieving product (Code: " + response.code() + ")"));
                }
            }

            @Override
            public void onFailure(Call<OpenFoodFactsResponse> call, Throwable t) {
                resultLiveData.setValue(Result.error("Network failure: " + (t.getMessage() != null ? t.getMessage() : "Unable to reach food database"), t));
            }
        });

        return resultLiveData;
    }

    private FoodProduct mapDtoToDomain(OpenFoodFactsProductDto dto, String fallbackBarcode) {
        FoodProduct product = new FoodProduct();
        product.setBarcode(dto.getCode() != null ? dto.getCode() : fallbackBarcode);
        product.setProductName(dto.getResolvedProductName());
        product.setBrand(dto.getBrands());
        product.setIngredients(dto.getResolvedIngredients());
        product.setServingSize(dto.getServingSize());
        product.setImageUrl(dto.getResolvedImageUrl());
        product.setNutritionGrade(dto.getNutritionGrades());
        product.setNovaGroup(dto.getNovaGroup());
        product.setAllergens(dto.getCleanAllergens());
        product.setCategories(dto.getCategoriesTags());

        Nutriments nutriments = new Nutriments();
        OpenFoodFactsNutrimentsDto nutrimentsDto = dto.getNutriments();
        if (nutrimentsDto != null) {
            nutriments.setCalories(nutrimentsDto.getCalories());
            nutriments.setSugars(nutrimentsDto.getSugars());
            nutriments.setSodium(nutrimentsDto.getSodiumMg());
            nutriments.setFats(nutrimentsDto.getFats());
            nutriments.setSaturatedFat(nutrimentsDto.getSaturatedFat());
            nutriments.setProteins(nutrimentsDto.getProteins());
            nutriments.setCarbohydrates(nutrimentsDto.getCarbohydrates());
            nutriments.setFiber(nutrimentsDto.getFiber());
            nutriments.setSalt(nutrimentsDto.getSalt());

            Log.d(TAG, String.format("Mapped Nutriments for %s: Cal=%.1f, Sugar=%.1f, Sodium=%.1f",
                    fallbackBarcode, nutriments.getCalories(), nutriments.getSugars(), nutriments.getSodium()));
        }
        product.setNutriments(nutriments);

        return product;
    }
}
