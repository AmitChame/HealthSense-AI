package com.healthsenseai.ui.auth;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.databinding.ActivitySplashBinding;
import com.healthsenseai.ui.home.MainActivity;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Splash Screen Activity.
 * Checks authentication state and routes user to MainActivity or LoginActivity.
 */
public class SplashActivity extends AppCompatActivity {

    private ActivitySplashBinding binding;
    private AuthViewModel authViewModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivitySplashBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        authViewModel = new ViewModelProvider(this, ViewModelFactory.getInstance()).get(AuthViewModel.class);

        // Delay slightly for branding presentation then route
        new Handler(Looper.getMainLooper()).postDelayed(this::checkAuthAndNavigate, 1200);
    }

    private void checkAuthAndNavigate() {
        if (isFinishing() || isDestroyed()) return;

        Intent intent;
        if (authViewModel.isUserLoggedIn()) {
            intent = new Intent(this, MainActivity.class);
        } else {
            intent = new Intent(this, LoginActivity.class);
        }
        startActivity(intent);
        finish();
    }
}
