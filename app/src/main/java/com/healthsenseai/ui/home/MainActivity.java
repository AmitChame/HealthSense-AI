package com.healthsenseai.ui.home;

import android.content.Intent;
import android.os.Bundle;
import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentTransaction;
import com.healthsenseai.R;
import com.healthsenseai.databinding.ActivityMainBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.family.FamilyListFragment;
import com.healthsenseai.ui.history.HistoryFragment;
import com.healthsenseai.ui.profile.ProfileFragment;
import com.healthsenseai.ui.scanner.ScannerActivity;

/**
 * Main Activity hosting the primary bottom navigation and fragment container.
 */
public class MainActivity extends BaseActivity {

    private ActivityMainBinding binding;
    private int currentSelectedItemId = R.id.nav_home;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        setupBottomNavigation();

        if (savedInstanceState == null) {
            loadFragment(new HomeFragment(), false);
        }
    }

    private void setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener(item -> {
            int itemId = item.getItemId();
            if (itemId == currentSelectedItemId && itemId != R.id.nav_scan) {
                return false;
            }

            if (itemId == R.id.nav_home) {
                currentSelectedItemId = itemId;
                loadFragment(new HomeFragment(), true);
                return true;
            } else if (itemId == R.id.nav_family) {
                currentSelectedItemId = itemId;
                loadFragment(new FamilyListFragment(), true);
                return true;
            } else if (itemId == R.id.nav_scan) {
                // Launch dedicated full-screen Scanner Activity
                Intent intent = new Intent(this, ScannerActivity.class);
                startActivity(intent);
                return false; // Do not switch bottom nav selected item permanently
            } else if (itemId == R.id.nav_history) {
                currentSelectedItemId = itemId;
                loadFragment(new HistoryFragment(), true);
                return true;
            } else if (itemId == R.id.nav_profile) {
                currentSelectedItemId = itemId;
                loadFragment(new ProfileFragment(), true);
                return true;
            }
            return false;
        });
    }

    public void navigateToFamilyTab() {
        binding.bottomNavigation.setSelectedItemId(R.id.nav_family);
    }

    public void navigateToHistoryTab() {
        binding.bottomNavigation.setSelectedItemId(R.id.nav_history);
    }

    private void loadFragment(@NonNull Fragment fragment, boolean animate) {
        FragmentTransaction transaction = getSupportFragmentManager().beginTransaction();
        if (animate) {
            transaction.setCustomAnimations(android.R.anim.fade_in, android.R.anim.fade_out);
        }
        transaction.replace(R.id.fragment_container, fragment);
        transaction.commit();
    }
}
