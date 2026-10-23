package com.healthsenseai.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.repository.FoodProductRepository;

/**
 * ViewModel managing food product barcode lookups and product details.
 */
public class FoodProductViewModel extends ViewModel {

    private final FoodProductRepository productRepository;
    private final MutableLiveData<Result<FoodProduct>> productResult = new MutableLiveData<>();
    private FoodProduct currentProduct;

    public FoodProductViewModel(FoodProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public LiveData<Result<FoodProduct>> getProductResult() {
        return productResult;
    }

    public void fetchProductByBarcode(String barcode) {
        productRepository.getProductByBarcode(barcode).observeForever(result -> {
            if (result != null && result.isSuccess()) {
                currentProduct = result.getData();
            }
            productResult.setValue(result);
        });
    }

    public FoodProduct getCurrentProduct() {
        return currentProduct;
    }

    public void setCurrentProduct(FoodProduct product) {
        this.currentProduct = product;
    }
}
