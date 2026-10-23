package com.healthsenseai.ui.product;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import androidx.appcompat.app.AlertDialog;
import androidx.lifecycle.ViewModelProvider;
import com.bumptech.glide.Glide;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.Nutriments;
import com.healthsenseai.databinding.ActivityProductDetailBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.family.AddEditFamilyMemberActivity;
import com.healthsenseai.ui.recommendation.RecommendationActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;
import java.util.List;

/**
 * Activity presenting packaged food product nutritional facts, ingredients, and allergens.
 */
public class ProductDetailActivity extends BaseActivity {

    private ActivityProductDetailBinding binding;
    private FoodProduct product;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityProductDetailBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(this, factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(this, factory).get(FamilyViewModel.class);

        if (getIntent().hasExtra(Constants.EXTRA_FOOD_PRODUCT)) {
            product = (FoodProduct) getIntent().getSerializableExtra(Constants.EXTRA_FOOD_PRODUCT);
        }

        if (product == null) {
            ViewUtils.showToast(this, "Product details unavailable");
            finish();
            return;
        }

        setupToolbar();
        populateProductData();
        setupAnalyzeAction();
    }

    private void setupToolbar() {
        binding.toolbar.setNavigationOnClickListener(v -> finish());
    }

    private void populateProductData() {
        binding.tvProductName.setText(product.getProductName());
        binding.tvProductBrand.setText(product.getBrand());
        binding.tvProductBarcode.setText(getString(R.string.label_barcode, product.getBarcode()));
        binding.tvServingSize.setText(getString(R.string.label_serving_size, product.getServingSize()));

        // Load Product Image
        if (product.getImageUrl() != null && !product.getImageUrl().isEmpty()) {
            Glide.with(this)
                    .load(product.getImageUrl())
                    .placeholder(R.drawable.ic_nutrition)
                    .error(R.drawable.ic_nutrition)
                    .fitCenter()
                    .into(binding.ivProductImage);
        } else {
            binding.ivProductImage.setImageResource(R.drawable.ic_nutrition);
        }

        // Nutrition Values
        Nutriments nutriments = product.getNutriments();
        binding.tvValCalories.setText(nutriments.getFormattedCalories());
        binding.tvValSugars.setText(nutriments.getFormattedSugars());
        binding.tvValSodium.setText(nutriments.getFormattedSodium());
        binding.tvValFat.setText(nutriments.getFormattedFats());
        binding.tvValSatFat.setText(nutriments.getFormattedSaturatedFat());
        binding.tvValProtein.setText(nutriments.getFormattedProteins());
        binding.tvValCarbs.setText(nutriments.getFormattedCarbohydrates());
        binding.tvValFiber.setText(nutriments.getFormattedFiber());

        // Allergens
        List<String> allergens = product.getAllergens();
        if (allergens != null && !allergens.isEmpty()) {
            binding.tvAllergensList.setText(String.join(", ", allergens));
        } else {
            binding.tvAllergensList.setText(R.string.no_allergens_listed);
        }

        // Ingredients
        binding.tvIngredientsList.setText(product.getIngredients());
    }

    private void setupAnalyzeAction() {
        binding.btnAnalyzeFamily.setOnClickListener(v -> checkFamilyAndAnalyze());
    }

    private void checkFamilyAndAnalyze() {
        String userId = authViewModel.getCurrentUserId();
        if (userId == null) {
            ViewUtils.showErrorSnackbar(binding.getRoot(), "Please sign in to run family recommendations");
            return;
        }

        showLoading("Checking family profiles…");
        familyViewModel.getFamilyMembers(userId).observe(this, result -> {
            if (result == null) return;
            hideLoading();

            if (result.isSuccess()) {
                List<FamilyMember> members = result.getData();
                if (members != null && !members.isEmpty()) {
                    Intent intent = new Intent(this, RecommendationActivity.class);
                    intent.putExtra(Constants.EXTRA_FOOD_PRODUCT, product);
                    startActivity(intent);
                } else {
                    promptAddFamilyMember();
                }
            } else if (result.isError()) {
                ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
            }
        });
    }

    private void promptAddFamilyMember() {
        new AlertDialog.Builder(this)
                .setTitle("No Family Profiles Found")
                .setMessage("To analyze this food product, please add at least one family member profile with their health conditions or allergies.")
                .setPositiveButton("Add Family Member", (dialog, which) -> {
                    Intent intent = new Intent(this, AddEditFamilyMemberActivity.class);
                    startActivity(intent);
                })
                .setNegativeButton(R.string.btn_cancel, null)
                .show();
    }
}
