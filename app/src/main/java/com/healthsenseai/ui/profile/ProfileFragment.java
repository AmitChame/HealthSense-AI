package com.healthsenseai.ui.profile;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.R;
import com.healthsenseai.data.local.AppPreferences;
import com.healthsenseai.databinding.FragmentProfileBinding;
import com.healthsenseai.ui.auth.LoginActivity;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Fragment for Profile management, FastAPI endpoint configuration, legal notices, and sign-out.
 */
public class ProfileFragment extends Fragment {

    private FragmentProfileBinding binding;
    private AuthViewModel authViewModel;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        binding = FragmentProfileBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(requireActivity(), factory).get(AuthViewModel.class);

        setupUserProfile();
        setupBackendConfiguration();
        setupLegalOptions();
        setupLogout();
    }

    private void setupUserProfile() {
        String userId = authViewModel.getCurrentUserId();
        if (userId != null) {
            authViewModel.getUserProfile(userId).observe(getViewLifecycleOwner(), result -> {
                if (result != null && result.isSuccess() && result.getData() != null) {
                    binding.tvProfileName.setText(result.getData().getName());
                    binding.tvProfileEmail.setText(result.getData().getEmail());
                    binding.tvUserAvatar.setText(ViewUtils.getInitials(result.getData().getName()));
                } else if (authViewModel.getCurrentFirebaseUser() != null) {
                    binding.tvProfileName.setText(authViewModel.getCurrentFirebaseUser().getDisplayName() != null ? authViewModel.getCurrentFirebaseUser().getDisplayName() : "HealthSense User");
                    binding.tvProfileEmail.setText(authViewModel.getCurrentFirebaseUser().getEmail());
                    binding.tvUserAvatar.setText(ViewUtils.getInitials(binding.tvProfileName.getText().toString()));
                }
            });
        }
    }

    private void setupBackendConfiguration() {
        updateBackendUrlLabel();

        binding.cardBackendUrl.setOnClickListener(v -> showBackendUrlDialog());
    }

    private void updateBackendUrlLabel() {
        String currentUrl = AppPreferences.getInstance().getFastApiBaseUrl();
        if (currentUrl != null && !currentUrl.trim().isEmpty()) {
            binding.tvCurrentBackendUrl.setText(currentUrl);
        } else {
            binding.tvCurrentBackendUrl.setText("Local Rule Engine (FastAPI offline)");
        }
    }

    private void showBackendUrlDialog() {
        View dialogView = LayoutInflater.from(requireContext()).inflate(R.layout.dialog_api_settings, null);
        EditText etUrl = dialogView.findViewById(R.id.et_backend_url);
        etUrl.setText(AppPreferences.getInstance().getFastApiBaseUrl());

        new AlertDialog.Builder(requireContext())
                .setView(dialogView)
                .setPositiveButton(R.string.btn_save, (dialog, which) -> {
                    String newUrl = etUrl.getText() != null ? etUrl.getText().toString().trim() : "";
                    AppPreferences.getInstance().setFastApiBaseUrl(newUrl);
                    updateBackendUrlLabel();
                    ViewUtils.showToast(requireContext(), "Backend URL updated");
                })
                .setNegativeButton(R.string.btn_cancel, null)
                .show();
    }

    private void setupLegalOptions() {
        binding.rowDisclaimer.setOnClickListener(v -> {
            new AlertDialog.Builder(requireContext())
                    .setTitle(R.string.medical_disclaimer_title)
                    .setMessage(R.string.medical_disclaimer_content)
                    .setPositiveButton(R.string.btn_close, null)
                    .show();
        });

        binding.rowPrivacy.setOnClickListener(v -> {
            new AlertDialog.Builder(requireContext())
                    .setTitle(R.string.privacy_policy_title)
                    .setMessage(R.string.privacy_policy_content)
                    .setPositiveButton(R.string.btn_close, null)
                    .show();
        });

        binding.rowAbout.setOnClickListener(v -> {
            new AlertDialog.Builder(requireContext())
                    .setTitle(R.string.app_name)
                    .setMessage(getString(R.string.app_description) + "\n\n" + getString(R.string.app_version) + "\nMCA Mini Project")
                    .setPositiveButton(R.string.btn_close, null)
                    .show();
        });
    }

    private void setupLogout() {
        binding.btnLogout.setOnClickListener(v -> {
            new AlertDialog.Builder(requireContext())
                    .setTitle(R.string.confirm_logout_title)
                    .setMessage(R.string.confirm_logout_msg)
                    .setPositiveButton(R.string.btn_logout, (dialog, which) -> {
                        authViewModel.logout();
                        Intent intent = new Intent(requireContext(), LoginActivity.class);
                        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                        startActivity(intent);
                        requireActivity().finish();
                    })
                    .setNegativeButton(R.string.btn_cancel, null)
                    .show();
        });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
