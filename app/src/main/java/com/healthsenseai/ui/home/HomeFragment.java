package com.healthsenseai.ui.home;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.databinding.FragmentHomeBinding;
import com.healthsenseai.ui.family.AddEditFamilyMemberActivity;
import com.healthsenseai.ui.family.FamilyMemberDetailActivity;
import com.healthsenseai.ui.home.adapter.HomeFamilyAdapter;
import com.healthsenseai.ui.home.adapter.RecentScansAdapter;
import com.healthsenseai.ui.recommendation.RecommendationActivity;
import com.healthsenseai.ui.scanner.ScannerActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.HistoryViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Home Dashboard Fragment displaying user stats, quick scan CTA, family preview, and recent scans.
 */
public class HomeFragment extends Fragment {

    private FragmentHomeBinding binding;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;
    private HistoryViewModel historyViewModel;

    private HomeFamilyAdapter familyAdapter;
    private RecentScansAdapter recentScansAdapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        binding = FragmentHomeBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(requireActivity(), factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(requireActivity(), factory).get(FamilyViewModel.class);
        historyViewModel = new ViewModelProvider(requireActivity(), factory).get(HistoryViewModel.class);

        setupRecyclerViews();
        setupListeners();
        observeData();
    }

    private void setupRecyclerViews() {
        // Horizontal Family RecyclerView
        familyAdapter = new HomeFamilyAdapter(member -> {
            Intent intent = new Intent(requireContext(), FamilyMemberDetailActivity.class);
            intent.putExtra(Constants.EXTRA_FAMILY_MEMBER, member);
            startActivity(intent);
        });
        binding.rvHomeFamily.setLayoutManager(
                new LinearLayoutManager(requireContext(), LinearLayoutManager.HORIZONTAL, false)
        );
        binding.rvHomeFamily.setAdapter(familyAdapter);

        // Recent Scans RecyclerView
        recentScansAdapter = new RecentScansAdapter(item -> {
            if (item.getFoodProduct() != null && item.getRecommendationResponse() != null) {
                Intent intent = new Intent(requireContext(), RecommendationActivity.class);
                intent.putExtra(Constants.EXTRA_FOOD_PRODUCT, item.getFoodProduct());
                intent.putExtra(Constants.EXTRA_RECOMMENDATION_RESPONSE, item.getRecommendationResponse());
                startActivity(intent);
            }
        });
        binding.rvRecentScans.setLayoutManager(new LinearLayoutManager(requireContext()));
        binding.rvRecentScans.setAdapter(recentScansAdapter);
    }

    private void setupListeners() {
        binding.btnHomeScan.setOnClickListener(v -> {
            Intent intent = new Intent(requireContext(), ScannerActivity.class);
            startActivity(intent);
        });

        binding.btnSeeAllFamily.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToFamilyTab();
            }
        });

        binding.btnHomeAddFamily.setOnClickListener(v -> {
            Intent intent = new Intent(requireContext(), AddEditFamilyMemberActivity.class);
            startActivity(intent);
        });

        binding.btnSeeAllScans.setOnClickListener(v -> {
            if (getActivity() instanceof MainActivity) {
                ((MainActivity) getActivity()).navigateToHistoryTab();
            }
        });
    }

    private void observeData() {
        String userId = authViewModel.getCurrentUserId();

        // 1. Observe User profile for Greeting
        if (userId != null) {
            authViewModel.getUserProfile(userId).observe(getViewLifecycleOwner(), userResult -> {
                if (userResult != null && userResult.isSuccess() && userResult.getData() != null) {
                    binding.tvGreeting.setText(getString(R.string.home_greeting, userResult.getData().getName()));
                } else if (authViewModel.getCurrentFirebaseUser() != null) {
                    String name = authViewModel.getCurrentFirebaseUser().getDisplayName();
                    if (name == null || name.isEmpty()) name = "Friend";
                    binding.tvGreeting.setText(getString(R.string.home_greeting, name));
                }
            });

            // 2. Observe Family Members
            familyViewModel.getFamilyMembers(userId).observe(getViewLifecycleOwner(), familyResult -> {
                if (familyResult != null && familyResult.isSuccess()) {
                    java.util.List<FamilyMember> members = familyResult.getData();
                    int count = members != null ? members.size() : 0;
                    binding.tvStatFamilyNumber.setText(String.valueOf(count));

                    if (count > 0) {
                        binding.rvHomeFamily.setVisibility(View.VISIBLE);
                        binding.cardEmptyFamily.setVisibility(View.GONE);
                        familyAdapter.setMembers(members);
                    } else {
                        binding.rvHomeFamily.setVisibility(View.GONE);
                        binding.cardEmptyFamily.setVisibility(View.VISIBLE);
                    }
                }
            });

            // 3. Observe Scan History
            historyViewModel.getScanHistory(userId).observe(getViewLifecycleOwner(), historyResult -> {
                if (historyResult != null && historyResult.isSuccess()) {
                    java.util.List<ScanHistoryItem> historyItems = historyResult.getData();
                    int count = historyItems != null ? historyItems.size() : 0;
                    binding.tvStatScansNumber.setText(String.valueOf(count));

                    if (count > 0) {
                        binding.rvRecentScans.setVisibility(View.VISIBLE);
                        binding.tvEmptyRecentScans.setVisibility(View.GONE);
                        recentScansAdapter.setItems(historyItems);
                    } else {
                        binding.rvRecentScans.setVisibility(View.GONE);
                        binding.tvEmptyRecentScans.setVisibility(View.VISIBLE);
                    }
                }
            });
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
