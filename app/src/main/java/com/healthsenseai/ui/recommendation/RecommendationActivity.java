package com.healthsenseai.ui.recommendation;

import android.content.res.ColorStateList;
import android.os.Bundle;
import android.view.View;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import com.bumptech.glide.Glide;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.databinding.ActivityRecommendationBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.recommendation.adapter.FamilyRecommendationAdapter;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.RecommendationViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;
import java.util.List;

/**
 * Activity presenting personalized food recommendations, suitability tiers, and risk factors for each family member.
 */
public class RecommendationActivity extends BaseActivity {

    private ActivityRecommendationBinding binding;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;
    private RecommendationViewModel recommendationViewModel;

    private FoodProduct product;
    private RecommendationResponse recommendationResponse;
    private FamilyRecommendationAdapter adapter;
    private boolean isAlreadySaved = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityRecommendationBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(this, factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(this, factory).get(FamilyViewModel.class);
        recommendationViewModel = new ViewModelProvider(this, factory).get(RecommendationViewModel.class);

        if (getIntent().hasExtra(Constants.EXTRA_FOOD_PRODUCT)) {
            product = (FoodProduct) getIntent().getSerializableExtra(Constants.EXTRA_FOOD_PRODUCT);
        }

        if (getIntent().hasExtra(Constants.EXTRA_RECOMMENDATION_RESPONSE)) {
            recommendationResponse = (RecommendationResponse) getIntent().getSerializableExtra(Constants.EXTRA_RECOMMENDATION_RESPONSE);
            isAlreadySaved = true; // Viewing from history
        }

        setupToolbar();
        setupRecyclerView();
        setupProductHeader();
        setupSaveButton();
        observeRecommendationState();

        if (recommendationResponse != null) {
            displayRecommendations(recommendationResponse);
        } else if (product != null) {
            startRecommendationAnalysis();
        } else {
            ViewUtils.showToast(this, "Recommendation data unavailable");
            finish();
        }
    }

    private void setupToolbar() {
        binding.toolbar.setNavigationOnClickListener(v -> finish());
    }

    private void setupRecyclerView() {
        adapter = new FamilyRecommendationAdapter();
        binding.rvRecommendations.setLayoutManager(new LinearLayoutManager(this));
        binding.rvRecommendations.setAdapter(adapter);
    }

    private void setupProductHeader() {
        if (product != null) {
            binding.tvRecProductName.setText(product.getProductName() != null ? product.getProductName() : "Unknown Product");
            binding.tvRecProductBrand.setText(product.getBrand() != null && !product.getBrand().isEmpty() 
                    ? product.getBrand() 
                    : (product.getBarcode() != null ? "Barcode: " + product.getBarcode() : "HealthSense AI"));

            if (product.getImageUrl() != null && !product.getImageUrl().isEmpty()) {
                Glide.with(this)
                        .load(product.getImageUrl())
                        .placeholder(R.drawable.ic_nutrition)
                        .error(R.drawable.ic_nutrition)
                        .fitCenter()
                        .into(binding.ivRecProduct);
            }
        } else if (recommendationResponse != null) {
            String name = recommendationResponse.getProductName();
            binding.tvRecProductName.setText(name != null && !name.isEmpty() ? name : "Analyzed Food Product");
            String barcode = recommendationResponse.getBarcode();
            binding.tvRecProductBrand.setText(barcode != null && !barcode.isEmpty() ? "Barcode: " + barcode : "Health Assessment");
        }
    }

    private void setupSaveButton() {
        if (isAlreadySaved) {
            binding.cardBottomSave.setVisibility(View.GONE);
        } else {
            binding.btnSaveHistory.setOnClickListener(v -> saveCurrentAnalysis());
        }
    }

    private void startRecommendationAnalysis() {
        String userId = authViewModel.getCurrentUserId();
        if (userId == null) {
            ViewUtils.showErrorSnackbar(binding.getRoot(), "User session expired");
            return;
        }

        binding.progressRecommendation.setVisibility(View.VISIBLE);

        familyViewModel.getFamilyMembers(userId).observe(this, familyResult -> {
            if (familyResult != null && familyResult.isSuccess()) {
                List<FamilyMember> members = familyResult.getData();
                if (members != null && !members.isEmpty()) {
                    recommendationViewModel.analyzeFoodForFamily(product, members);
                } else {
                    binding.progressRecommendation.setVisibility(View.GONE);
                    binding.tvEmptyRecommendations.setVisibility(View.VISIBLE);
                    binding.rvRecommendations.setVisibility(View.GONE);
                }
            }
        });
    }

    private void observeRecommendationState() {
        recommendationViewModel.getRecommendationResult().observe(this, result -> {
            if (result == null) return;

            if (result.isLoading()) {
                binding.progressRecommendation.setVisibility(View.VISIBLE);
            } else if (result.isSuccess()) {
                binding.progressRecommendation.setVisibility(View.GONE);
                recommendationResponse = result.getData();
                if (recommendationResponse != null) {
                    displayRecommendations(recommendationResponse);
                }
            } else if (result.isError()) {
                binding.progressRecommendation.setVisibility(View.GONE);
                ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
            }
        });

        recommendationViewModel.getSaveHistoryResult().observe(this, saveResult -> {
            if (saveResult == null) return;

            if (saveResult.isSuccess()) {
                isAlreadySaved = true;
                ViewUtils.showToast(this, getString(R.string.msg_scan_saved));
                binding.btnSaveHistory.setEnabled(false);
                binding.btnSaveHistory.setText("Saved in History");
                binding.btnSaveHistory.setIconResource(R.drawable.ic_check_circle);
            } else if (saveResult.isError()) {
                binding.btnSaveHistory.setEnabled(true);
                ViewUtils.showErrorSnackbar(binding.getRoot(), saveResult.getMessage());
            }
        });
    }

    private void displayRecommendations(RecommendationResponse response) {
        if (response == null) return;

        // If product was null originally, update header from response
        if (product == null) {
            setupProductHeader();
        }

        // 1. Food Grade Badge with dynamic color
        String grade = response.getFoodGrade() != null ? response.getFoodGrade().trim().toUpperCase() : "B";
        if (grade.contains("INSUFFICIENT")) {
            binding.tvRecGradeBadge.setText("INSUFFICIENT DATA");
        } else {
            binding.tvRecGradeBadge.setText("GRADE " + grade);
        }

        int gradeBgColor;
        int gradeTextColor;
        switch (grade) {
            case "A":
                gradeBgColor = ContextCompat.getColor(this, R.color.status_suitable_bg);
                gradeTextColor = ContextCompat.getColor(this, R.color.status_suitable_text);
                break;
            case "B":
                gradeBgColor = ContextCompat.getColor(this, R.color.primary_container);
                gradeTextColor = ContextCompat.getColor(this, R.color.primary_dark);
                break;
            case "C":
                gradeBgColor = ContextCompat.getColor(this, R.color.status_caution_bg);
                gradeTextColor = ContextCompat.getColor(this, R.color.status_caution_text);
                break;
            case "D":
            case "E":
                gradeBgColor = ContextCompat.getColor(this, R.color.status_danger_bg);
                gradeTextColor = ContextCompat.getColor(this, R.color.status_danger_text);
                break;
            default:
                gradeBgColor = ContextCompat.getColor(this, R.color.surface_variant);
                gradeTextColor = ContextCompat.getColor(this, R.color.text_secondary);
                break;
        }
        binding.tvRecGradeBadge.setBackgroundTintList(ColorStateList.valueOf(gradeBgColor));
        binding.tvRecGradeBadge.setTextColor(gradeTextColor);

        // 2. Assessment Source Badge
        String src = response.getSource() != null ? response.getSource().toUpperCase() : "";
        boolean isRemote = src.contains("REMOTE");
        if (isRemote) {
            String model = response.getActiveModel() != null ? response.getActiveModel() : "HealthSense V2";
            binding.tvRecSourceBadge.setText("⚡ " + model);
            binding.tvRecSourceBadge.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(this, R.color.primary_container)));
            binding.tvRecSourceBadge.setTextColor(ContextCompat.getColor(this, R.color.primary_dark));
        } else {
            String model = response.getActiveModel() != null ? response.getActiveModel() : "Offline Analysis";
            binding.tvRecSourceBadge.setText("🛡️ " + model);
            binding.tvRecSourceBadge.setBackgroundTintList(ColorStateList.valueOf(ContextCompat.getColor(this, R.color.secondary_container)));
            binding.tvRecSourceBadge.setTextColor(ContextCompat.getColor(this, R.color.secondary_dark));
        }

        // 3. Frequency Badge with dynamic color
        String freq = response.getFrequencyRecommendation() != null ? response.getFrequencyRecommendation().trim().toUpperCase() : "OCCASIONAL";
        binding.tvRecFrequencyBadge.setText(freq);
        int freqBgColor;
        int freqTextColor;
        if ("REGULAR".equalsIgnoreCase(freq) || "DAILY".equalsIgnoreCase(freq)) {
            freqBgColor = ContextCompat.getColor(this, R.color.status_suitable_bg);
            freqTextColor = ContextCompat.getColor(this, R.color.status_suitable_text);
        } else if ("OCCASIONAL".equalsIgnoreCase(freq)) {
            freqBgColor = ContextCompat.getColor(this, R.color.primary_container);
            freqTextColor = ContextCompat.getColor(this, R.color.primary_dark);
        } else if ("LIMIT".equalsIgnoreCase(freq) || "LIMIT FREQUENCY".equalsIgnoreCase(freq)) {
            freqBgColor = ContextCompat.getColor(this, R.color.status_caution_bg);
            freqTextColor = ContextCompat.getColor(this, R.color.status_caution_text);
        } else if ("AVOID".equalsIgnoreCase(freq)) {
            freqBgColor = ContextCompat.getColor(this, R.color.status_danger_bg);
            freqTextColor = ContextCompat.getColor(this, R.color.status_danger_text);
        } else {
            freqBgColor = ContextCompat.getColor(this, R.color.surface_variant);
            freqTextColor = ContextCompat.getColor(this, R.color.text_secondary);
        }
        binding.tvRecFrequencyBadge.setBackgroundTintList(ColorStateList.valueOf(freqBgColor));
        binding.tvRecFrequencyBadge.setTextColor(freqTextColor);

        // 4. Assessment Confidence Badge
        String conf = response.getAssessmentConfidence() != null ? response.getAssessmentConfidence().trim().toUpperCase() : "HIGH";
        binding.tvRecConfidenceBadge.setText(conf + " Conf.");

        // 5. Overall Verdict
        if (response.getOverallVerdict() != null && !response.getOverallVerdict().isEmpty()) {
            binding.tvRecOverallVerdict.setText(response.getOverallVerdict());
            binding.tvRecOverallVerdict.setVisibility(View.VISIBLE);
        }

        // 6. List of Recommendations
        if (response.getRecommendations() != null && !response.getRecommendations().isEmpty()) {
            binding.rvRecommendations.setVisibility(View.VISIBLE);
            binding.tvEmptyRecommendations.setVisibility(View.GONE);
            adapter.setRecommendations(response.getRecommendations());
        } else {
            binding.rvRecommendations.setVisibility(View.GONE);
            binding.tvEmptyRecommendations.setVisibility(View.VISIBLE);
        }
    }

    private void saveCurrentAnalysis() {
        if (isAlreadySaved) return;

        String userId = authViewModel.getCurrentUserId();
        if (userId != null && product != null && recommendationResponse != null) {
            binding.btnSaveHistory.setEnabled(false);
            recommendationViewModel.saveToHistory(userId, product, recommendationResponse);
        }
    }
}
