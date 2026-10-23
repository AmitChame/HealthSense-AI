package com.healthsenseai.ui.auth;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Patterns;
import android.view.View;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.R;
import com.healthsenseai.databinding.ActivityLoginBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.home.MainActivity;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Login Activity handling user email/password sign-in.
 */
public class LoginActivity extends BaseActivity {

    private ActivityLoginBinding binding;
    private AuthViewModel authViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityLoginBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        authViewModel = new ViewModelProvider(this, ViewModelFactory.getInstance()).get(AuthViewModel.class);

        setupListeners();
        observeViewModel();
    }

    private void setupListeners() {
        binding.btnLogin.setOnClickListener(v -> performLogin());

        binding.tvForgotPassword.setOnClickListener(v -> {
            Intent intent = new Intent(this, ForgotPasswordActivity.class);
            startActivity(intent);
        });

        binding.tvGoToRegister.setOnClickListener(v -> {
            Intent intent = new Intent(this, RegisterActivity.class);
            startActivity(intent);
        });
    }

    private void performLogin() {
        ViewUtils.hideKeyboard(this);

        String email = binding.etEmail.getText() != null ? binding.etEmail.getText().toString().trim() : "";
        String password = binding.etPassword.getText() != null ? binding.etPassword.getText().toString() : "";

        // Reset errors
        binding.tilEmail.setError(null);
        binding.tilPassword.setError(null);

        // Validation
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

        setLoading(true);
        authViewModel.login(email, password);
    }

    private void observeViewModel() {
        authViewModel.getLoginResult().observe(this, result -> {
            if (result == null) return;

            if (result.isLoading()) {
                setLoading(true);
            } else if (result.isSuccess()) {
                setLoading(false);
                ViewUtils.showToast(this, getString(R.string.msg_login_success));
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
        binding.btnLogin.setEnabled(!loading);
        binding.progressLogin.setVisibility(loading ? View.VISIBLE : View.GONE);
    }
}
