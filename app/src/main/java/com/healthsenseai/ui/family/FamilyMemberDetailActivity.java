package com.healthsenseai.ui.family;

import android.content.Intent;
import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.ViewModelProvider;
import com.google.android.material.chip.Chip;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.databinding.ActivityFamilyMemberDetailBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Activity presenting comprehensive health profile information for a selected family member.
 */
public class FamilyMemberDetailActivity extends BaseActivity {

    private ActivityFamilyMemberDetailBinding binding;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;
    private FamilyMember currentMember;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityFamilyMemberDetailBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(this, factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(this, factory).get(FamilyViewModel.class);

        if (getIntent().hasExtra(Constants.EXTRA_FAMILY_MEMBER)) {
            currentMember = (FamilyMember) getIntent().getSerializableExtra(Constants.EXTRA_FAMILY_MEMBER);
        }

        if (currentMember == null) {
            ViewUtils.showToast(this, "Family member profile not available");
            finish();
            return;
        }

        setupToolbar();
        populateData();
    }

    private void setupToolbar() {
        binding.toolbar.setNavigationOnClickListener(v -> finish());
        binding.toolbar.setOnMenuItemClickListener(item -> {
            int id = item.getItemId();
            if (id == R.id.action_edit) {
                Intent intent = new Intent(this, AddEditFamilyMemberActivity.class);
                intent.putExtra(Constants.EXTRA_FAMILY_MEMBER, currentMember);
                startActivity(intent);
                finish(); // Close detail to refresh after edit
                return true;
            } else if (id == R.id.action_delete) {
                confirmDelete();
                return true;
            }
            return false;
        });
    }

    private void populateData() {
        binding.tvDetailName.setText(currentMember.getName());
        binding.tvAvatar.setText(ViewUtils.getInitials(currentMember.getName()));
        binding.tvDetailAge.setText(currentMember.getAge() + " Years Old");
        binding.tvDetailGender.setText(currentMember.getGender() != null ? currentMember.getGender() : "Not specified");

        // Health Conditions
        binding.chipGroupConditionsDisplay.removeAllViews();
        if (currentMember.getHealthConditions() != null && !currentMember.getHealthConditions().isEmpty()) {
            for (String cond : currentMember.getHealthConditions()) {
                if (cond.equalsIgnoreCase("None")) continue;
                Chip chip = createDisplayChip(cond, R.color.surface_variant, R.color.text_primary);
                binding.chipGroupConditionsDisplay.addView(chip);
            }
        }
        if (binding.chipGroupConditionsDisplay.getChildCount() == 0) {
            Chip chip = createDisplayChip("No chronic conditions recorded", R.color.surface_variant, R.color.text_secondary);
            binding.chipGroupConditionsDisplay.addView(chip);
        }

        // Allergies
        binding.chipGroupAllergiesDisplay.removeAllViews();
        if (currentMember.getAllergies() != null && !currentMember.getAllergies().isEmpty()) {
            for (String allergy : currentMember.getAllergies()) {
                if (allergy.equalsIgnoreCase("None")) continue;
                Chip chip = createDisplayChip("⚠️ " + allergy, R.color.status_danger_bg, R.color.status_danger_text);
                chip.setChipStrokeColorResource(R.color.status_danger_stroke);
                chip.setChipStrokeWidth(1f);
                binding.chipGroupAllergiesDisplay.addView(chip);
            }
        }
        if (binding.chipGroupAllergiesDisplay.getChildCount() == 0) {
            Chip chip = createDisplayChip("No known food allergies", R.color.surface_variant, R.color.text_secondary);
            binding.chipGroupAllergiesDisplay.addView(chip);
        }

        // Dietary Preferences
        binding.chipGroupDietaryDisplay.removeAllViews();
        if (currentMember.getDietaryPreferences() != null && !currentMember.getDietaryPreferences().isEmpty()) {
            for (String diet : currentMember.getDietaryPreferences()) {
                Chip chip = createDisplayChip(diet, R.color.primary_container, R.color.primary_dark);
                binding.chipGroupDietaryDisplay.addView(chip);
            }
        }
        if (binding.chipGroupDietaryDisplay.getChildCount() == 0) {
            Chip chip = createDisplayChip("Standard balanced diet", R.color.surface_variant, R.color.text_secondary);
            binding.chipGroupDietaryDisplay.addView(chip);
        }

        // Notes
        if (currentMember.getNotes() != null && !currentMember.getNotes().trim().isEmpty()) {
            binding.tvDetailNotes.setText(currentMember.getNotes());
        } else {
            binding.tvDetailNotes.setText("No special doctor notes or dietary instructions.");
        }
    }

    private Chip createDisplayChip(String text, int bgRes, int textRes) {
        Chip chip = new Chip(this);
        chip.setText(text);
        chip.setCheckable(false);
        chip.setClickable(false);
        chip.setChipBackgroundColorResource(bgRes);
        chip.setTextColor(ContextCompat.getColor(this, textRes));
        chip.setTextSize(12f);
        return chip;
    }

    private void confirmDelete() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.confirm_delete_member_title)
                .setMessage(getString(R.string.confirm_delete_member_msg, currentMember.getName()))
                .setPositiveButton(R.string.btn_delete_member, (dialog, which) -> deleteMember())
                .setNegativeButton(R.string.btn_cancel, null)
                .show();
    }

    private void deleteMember() {
        String userId = authViewModel.getCurrentUserId();
        if (userId == null || currentMember.getId() == null) return;

        showLoading("Deleting profile…");
        familyViewModel.deleteFamilyMember(userId, currentMember.getId()).observe(this, result -> {
            if (result == null) return;
            hideLoading();
            if (result.isSuccess()) {
                ViewUtils.showToast(this, getString(R.string.member_deleted_success));
                finish();
            } else if (result.isError()) {
                ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
            }
        });
    }
}
