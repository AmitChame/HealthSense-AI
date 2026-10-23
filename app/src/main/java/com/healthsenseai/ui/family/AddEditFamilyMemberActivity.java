package com.healthsenseai.ui.family;

import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.ArrayAdapter;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.ViewModelProvider;
import com.google.android.material.chip.Chip;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.databinding.ActivityAddEditFamilyMemberBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;
import java.util.ArrayList;
import java.util.List;

/**
 * Activity for creating or updating a family member's health profile.
 */
public class AddEditFamilyMemberActivity extends BaseActivity {

    private ActivityAddEditFamilyMemberBinding binding;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;

    private FamilyMember existingMember;
    private boolean isEditMode = false;

    private final List<String> selectedConditions = new ArrayList<>();
    private final List<String> selectedAllergies = new ArrayList<>();
    private final List<String> selectedDietary = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityAddEditFamilyMemberBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(this, factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(this, factory).get(FamilyViewModel.class);

        if (getIntent().hasExtra(Constants.EXTRA_FAMILY_MEMBER)) {
            existingMember = (FamilyMember) getIntent().getSerializableExtra(Constants.EXTRA_FAMILY_MEMBER);
            if (existingMember != null) {
                isEditMode = true;
                binding.toolbar.setTitle(R.string.edit_member_title);
                if (existingMember.getHealthConditions() != null) {
                    selectedConditions.addAll(existingMember.getHealthConditions());
                }
                if (existingMember.getAllergies() != null) {
                    selectedAllergies.addAll(existingMember.getAllergies());
                }
                if (existingMember.getDietaryPreferences() != null) {
                    selectedDietary.addAll(existingMember.getDietaryPreferences());
                }
            }
        }

        setupToolbar();
        setupGenderDropdown();
        setupChipGroups();
        setupCustomInputs();
        setupSaveButton();

        if (isEditMode) {
            populateExistingData();
        }
    }

    private void setupToolbar() {
        binding.toolbar.setNavigationOnClickListener(v -> finish());
    }

    private void setupGenderDropdown() {
        String[] genders = getResources().getStringArray(R.array.genders);
        ArrayAdapter<String> genderAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, genders);
        binding.actvGender.setAdapter(genderAdapter);
        if (!isEditMode) {
            binding.actvGender.setText(genders[0], false);
        }
    }

    private void setupChipGroups() {
        // Health Conditions
        String[] conditions = getResources().getStringArray(R.array.common_health_conditions);
        for (String cond : conditions) {
            addFilterChip(binding.chipGroupConditions, cond, selectedConditions);
        }

        // Allergies
        String[] allergies = getResources().getStringArray(R.array.common_allergies);
        for (String allergy : allergies) {
            addFilterChip(binding.chipGroupAllergies, allergy, selectedAllergies);
        }

        // Dietary Preferences
        String[] dietary = getResources().getStringArray(R.array.dietary_preferences);
        for (String diet : dietary) {
            addFilterChip(binding.chipGroupDietary, diet, selectedDietary);
        }
    }

    private void addFilterChip(com.google.android.material.chip.ChipGroup group, String title, List<String> selectionList) {
        Chip chip = new Chip(this);
        chip.setText(title);
        chip.setCheckable(true);
        chip.setChecked(selectionList.contains(title));

        chip.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                if (title.equalsIgnoreCase("None")) {
                    // If None selected, uncheck other chips in the group
                    selectionList.clear();
                    selectionList.add(title);
                    for (int i = 0; i < group.getChildCount(); i++) {
                        Chip otherChip = (Chip) group.getChildAt(i);
                        if (otherChip != chip) {
                            otherChip.setChecked(false);
                        }
                    }
                } else {
                    selectionList.remove("None");
                    for (int i = 0; i < group.getChildCount(); i++) {
                        Chip otherChip = (Chip) group.getChildAt(i);
                        if (otherChip.getText().toString().equalsIgnoreCase("None")) {
                            otherChip.setChecked(false);
                        }
                    }
                    if (!selectionList.contains(title)) {
                        selectionList.add(title);
                    }
                }
            } else {
                selectionList.remove(title);
            }
        });

        group.addView(chip);
    }

    private void setupCustomInputs() {
        binding.btnAddCustomCondition.setOnClickListener(v -> {
            String custom = binding.etCustomCondition.getText() != null ? binding.etCustomCondition.getText().toString().trim() : "";
            if (!custom.isEmpty() && !selectedConditions.contains(custom)) {
                selectedConditions.add(custom);
                addFilterChip(binding.chipGroupConditions, custom, selectedConditions);
                binding.etCustomCondition.setText("");
            }
        });

        binding.btnAddCustomAllergy.setOnClickListener(v -> {
            String custom = binding.etCustomAllergy.getText() != null ? binding.etCustomAllergy.getText().toString().trim() : "";
            if (!custom.isEmpty() && !selectedAllergies.contains(custom)) {
                selectedAllergies.add(custom);
                addFilterChip(binding.chipGroupAllergies, custom, selectedAllergies);
                binding.etCustomAllergy.setText("");
            }
        });
    }

    private void populateExistingData() {
        binding.etName.setText(existingMember.getName());
        binding.etAge.setText(String.valueOf(existingMember.getAge()));
        if (existingMember.getGender() != null) {
            binding.actvGender.setText(existingMember.getGender(), false);
        }
        if (existingMember.getNotes() != null) {
            binding.etNotes.setText(existingMember.getNotes());
        }

        // Add any custom items that were not in predefined arrays
        for (String cond : selectedConditions) {
            boolean found = false;
            for (int i = 0; i < binding.chipGroupConditions.getChildCount(); i++) {
                Chip chip = (Chip) binding.chipGroupConditions.getChildAt(i);
                if (chip.getText().toString().equalsIgnoreCase(cond)) {
                    chip.setChecked(true);
                    found = true;
                    break;
                }
            }
            if (!found) {
                addFilterChip(binding.chipGroupConditions, cond, selectedConditions);
            }
        }

        for (String allergy : selectedAllergies) {
            boolean found = false;
            for (int i = 0; i < binding.chipGroupAllergies.getChildCount(); i++) {
                Chip chip = (Chip) binding.chipGroupAllergies.getChildAt(i);
                if (chip.getText().toString().equalsIgnoreCase(allergy)) {
                    chip.setChecked(true);
                    found = true;
                    break;
                }
            }
            if (!found) {
                addFilterChip(binding.chipGroupAllergies, allergy, selectedAllergies);
            }
        }
    }

    private void setupSaveButton() {
        binding.btnSaveMember.setOnClickListener(v -> saveMemberProfile());
    }

    private void saveMemberProfile() {
        ViewUtils.hideKeyboard(this);

        String name = binding.etName.getText() != null ? binding.etName.getText().toString().trim() : "";
        String ageStr = binding.etAge.getText() != null ? binding.etAge.getText().toString().trim() : "";
        String gender = binding.actvGender.getText() != null ? binding.actvGender.getText().toString() : "Other";
        String notes = binding.etNotes.getText() != null ? binding.etNotes.getText().toString().trim() : "";

        binding.tilName.setError(null);
        binding.tilAge.setError(null);

        if (TextUtils.isEmpty(name)) {
            binding.tilName.setError(getString(R.string.err_empty_name));
            binding.etName.requestFocus();
            return;
        }

        int age;
        try {
            age = Integer.parseInt(ageStr);
            if (age <= 0 || age > 120) {
                binding.tilAge.setError(getString(R.string.err_invalid_age));
                binding.etAge.requestFocus();
                return;
            }
        } catch (NumberFormatException e) {
            binding.tilAge.setError(getString(R.string.err_invalid_age));
            binding.etAge.requestFocus();
            return;
        }

        String userId = authViewModel.getCurrentUserId();
        if (userId == null) {
            ViewUtils.showErrorSnackbar(binding.getRoot(), "User authentication session expired. Please sign in again.");
            return;
        }

        setLoading(true);

        FamilyMember memberToSave = isEditMode ? existingMember : new FamilyMember();
        memberToSave.setName(name);
        memberToSave.setAge(age);
        memberToSave.setGender(gender);
        memberToSave.setHealthConditions(new ArrayList<>(selectedConditions));
        memberToSave.setAllergies(new ArrayList<>(selectedAllergies));
        memberToSave.setDietaryPreferences(new ArrayList<>(selectedDietary));
        memberToSave.setNotes(notes);

        if (isEditMode) {
            familyViewModel.updateFamilyMember(userId, memberToSave).observe(this, result -> {
                if (result == null) return;
                setLoading(false);
                if (result.isSuccess()) {
                    ViewUtils.showToast(this, getString(R.string.member_saved_success));
                    finish();
                } else if (result.isError()) {
                    ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
                }
            });
        } else {
            familyViewModel.addFamilyMember(userId, memberToSave).observe(this, result -> {
                if (result == null) return;
                setLoading(false);
                if (result.isSuccess()) {
                    ViewUtils.showToast(this, getString(R.string.member_saved_success));
                    finish();
                } else if (result.isError()) {
                    ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
                }
            });
        }
    }

    private void setLoading(boolean loading) {
        binding.btnSaveMember.setEnabled(!loading);
        binding.progressSave.setVisibility(loading ? View.VISIBLE : View.GONE);
    }
}
