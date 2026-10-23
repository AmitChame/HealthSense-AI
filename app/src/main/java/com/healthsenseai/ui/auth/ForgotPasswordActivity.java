package com.healthsenseai.ui.auth;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.Patterns;
import android.view.View;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.R;
import com.healthsenseai.databinding.ActivityForgotPasswordBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Forgot Password Activity for triggering Firebase password reset emails.
 */
public class ForgotPasswordActivity extends BaseActivity {

    private ActivityForgotPasswordBinding binding;
    private AuthViewModel authViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityForgotPasswordBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        authViewModel = new ViewModelProvider(this, ViewModelFactory.getInstance()).get(AuthViewModel.class);

        setupListeners();
        observeViewModel();
    }

    private void setupListeners() {
        binding.btnBack.setOnClickListener(v -> finish());
        binding.btnSendReset.setOnClickListener(v -> performPasswordReset());
    }

    private void performPasswordReset() {
        ViewUtils.hideKeyboard(this);

        String email = binding.etEmail.getText() != null ? binding.etEmail.getText().toString().trim() : "";
        binding.tilEmail.setError(null);

        if (TextUtils.isEmpty(email) || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.tilEmail.setError(getString(R.string.err_invalid_email));
            binding.etEmail.requestFocus();
            return;
        }

        setLoading(true);
        authViewModel.sendPasswordReset(email);
    }

    private void observeViewModel() {
        authViewModel.getPasswordResetResult().observe(this, result -> {
            if (result == null) return;

            if (result.isLoading()) {
                setLoading(true);
            } else if (result.isSuccess()) {
                setLoading(false);
                ViewUtils.showToast(this, getString(R.string.msg_password_reset_sent));
                finish();
            } else if (result.isError()) {
                setLoading(false);
                ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
            }
        });
    }

    private void setLoading(boolean loading) {
        binding.btnSendReset.setEnabled(!loading);
        binding.progressReset.setVisibility(loading ? View.VISIBLE : View.GONE);
    }
}
