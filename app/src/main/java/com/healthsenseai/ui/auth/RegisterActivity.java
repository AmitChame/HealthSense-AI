package com.healthsenseai.ui.auth;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Patterns;
import android.view.View;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.R;
import com.healthsenseai.databinding.ActivityRegisterBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.home.MainActivity;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Register Activity handling user registration and Firestore profile initialization.
 */
public class RegisterActivity extends BaseActivity {

    private ActivityRegisterBinding binding;
    private AuthViewModel authViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityRegisterBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        authViewModel = new ViewModelProvider(this, ViewModelFactory.getInstance()).get(AuthViewModel.class);

        setupListeners();
        observeViewModel();
    }

    private void setupListeners() {
        binding.btnRegister.setOnClickListener(v -> performRegister());

        binding.tvGoToLogin.setOnClickListener(v -> {
            finish();
        });
    }

    private void performRegister() {
        ViewUtils.hideKeyboard(this);

        String name = binding.etName.getText() != null ? binding.etName.getText().toString().trim() : "";
        String email = binding.etEmail.getText() != null ? binding.etEmail.getText().toString().trim() : "";
        String password = binding.etPassword.getText() != null ? binding.etPassword.getText().toString() : "";
        String confirmPassword = binding.etConfirmPassword.getText() != null ? binding.etConfirmPassword.getText().toString() : "";

        // Reset errors
        binding.tilName.setError(null);
        binding.tilEmail.setError(null);
        binding.tilPassword.setError(null);
        binding.tilConfirmPassword.setError(null);

        // Validation
        if (TextUtils.isEmpty(name)) {
            binding.tilName.setError(getString(R.string.err_empty_name));
            binding.etName.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(email) || !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.tilEmail.setError(getString(R.string.err_invalid_email));
            binding.etEmail.requestFocus();
            return;
        }

        if (TextUtils.isEmpty(password) || password.length() < 6) {
            binding.tilPassword.setError(getString(R.string.err_short_password));
            binding.etPassword.requestFocus();
            return;
        }

        if (!password.equals(confirmPassword)) {
            binding.tilConfirmPassword.setError(getString(R.string.err_password_mismatch));
            binding.etConfirmPassword.requestFocus();
            return;
        }

        setLoading(true);
        authViewModel.register(name, email, password);
    }

    private void observeViewModel() {
        authViewModel.getRegisterResult().observe(this, result -> {
            if (result == null) return;

            if (result.isLoading()) {
                setLoading(true);
            } else if (result.isSuccess()) {
                setLoading(false);
                ViewUtils.showToast(this, getString(R.string.msg_register_success));
                Intent intent = new Intent(this, MainActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                startActivity(intent);
                finish();
            } else if (result.isError()) {
                setLoading(false);
                ViewUtils.showErrorSnackbar(binding.getRoot(), result.getMessage());
            }
        });
    }

    private void setLoading(boolean loading) {
        binding.btnRegister.setEnabled(!loading);
        binding.progressRegister.setVisibility(loading ? View.VISIBLE : View.GONE);
    }
}
