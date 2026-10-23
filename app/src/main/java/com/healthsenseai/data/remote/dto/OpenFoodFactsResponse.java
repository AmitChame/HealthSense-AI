package com.healthsenseai.data.remote.dto;

import com.google.gson.annotations.SerializedName;
import java.io.Serializable;

/**
 * Root response from OpenFoodFacts API (e.g. GET /api/v0/product/{barcode}.json).
 */
public class OpenFoodFactsResponse implements Serializable {

    @SerializedName("status")
    private int status; // 1 = found, 0 = not found

    @SerializedName("status_verbose")
    private String statusVerbose;

    @SerializedName("code")
    private String code;

    @SerializedName("product")
    private OpenFoodFactsProductDto product;

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getStatusVerbose() {
        return statusVerbose;
    }

    public void setStatusVerbose(String statusVerbose) {
        this.statusVerbose = statusVerbose;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public OpenFoodFactsProductDto getProduct() {
        return product;
    }

    public void setProduct(OpenFoodFactsProductDto product) {
        this.product = product;
    }

    public boolean isFound() {
        return status == 1 && product != null;
    }
}
