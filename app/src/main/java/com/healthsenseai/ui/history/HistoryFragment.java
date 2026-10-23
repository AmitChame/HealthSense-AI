package com.healthsenseai.ui.history;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import com.healthsenseai.R;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.databinding.FragmentHistoryBinding;
import com.healthsenseai.ui.history.adapter.ScanHistoryAdapter;
import com.healthsenseai.ui.recommendation.RecommendationActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.HistoryViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;
import java.util.List;

/**
 * Fragment displaying past food product scans and saved family assessments.
 */
public class HistoryFragment extends Fragment {

    private FragmentHistoryBinding binding;
    private AuthViewModel authViewModel;
    private HistoryViewModel historyViewModel;
    private ScanHistoryAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        binding = FragmentHistoryBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(requireActivity(), factory).get(AuthViewModel.class);
        historyViewModel = new ViewModelProvider(requireActivity(), factory).get(HistoryViewModel.class);

        setupToolbar();
        setupRecyclerView();
        observeHistory();
    }

    private void setupToolbar() {
        binding.toolbar.setOnMenuItemClickListener(item -> {
            if (item.getItemId() == R.id.action_clear_history) {
                confirmClearHistory();
                return true;
            }
            return false;
        });
    }

    private void setupRecyclerView() {
        adapter = new ScanHistoryAdapter(new ScanHistoryAdapter.OnHistoryActionListener() {
            @Override
            public void onItemClick(ScanHistoryItem item) {
                if (item.getFoodProduct() != null && item.getRecommendationResponse() != null) {
                    Intent intent = new Intent(requireContext(), RecommendationActivity.class);
                    intent.putExtra(Constants.EXTRA_FOOD_PRODUCT, item.getFoodProduct());
                    intent.putExtra(Constants.EXTRA_RECOMMENDATION_RESPONSE, item.getRecommendationResponse());
                    startActivity(intent);
                } else {
                    ViewUtils.showToast(requireContext(), "Full scan data not cached for this record");
                }
            }

            @Override
            public void onDeleteClick(ScanHistoryItem item) {
                confirmDeleteItem(item);
            }
        });

        binding.rvHistory.setLayoutManager(new LinearLayoutManager(requireContext()));
        binding.rvHistory.setAdapter(adapter);
    }

    private void observeHistory() {
        String userId = authViewModel.getCurrentUserId();
        if (userId != null) {
            historyViewModel.getScanHistory(userId).observe(getViewLifecycleOwner(), result -> {
                if (result == null) return;

                if (result.isLoading()) {
                    binding.progressHistory.setVisibility(View.VISIBLE);
                } else if (result.isSuccess()) {
                    binding.progressHistory.setVisibility(View.GONE);
                    List<ScanHistoryItem> list = result.getData();
                    if (list != null && !list.isEmpty()) {
                        binding.rvHistory.setVisibility(View.VISIBLE);
                        binding.layoutEmptyHistory.setVisibility(View.GONE);
                        adapter.setItems(list);
                    } else {
                        binding.rvHistory.setVisibility(View.GONE);
                        binding.layoutEmptyHistory.setVisibility(View.VISIBLE);
                    }
                } else if (result.isError()) {
                    binding.progressHistory.setVisibility(View.GONE);
                }
            });
        }
    }

    private void confirmDeleteItem(ScanHistoryItem item) {
        new AlertDialog.Builder(requireContext())
                .setTitle("Delete Scan Entry?")
                .setMessage("Are you sure you want to remove '" + item.getProductName() + "' from your history?")
                .setPositiveButton("Delete", (dialog, which) -> {
                    String userId = authViewModel.getCurrentUserId();
                    if (userId != null && item.getId() != null) {
                        historyViewModel.deleteHistoryItem(userId, item.getId());
                    }
                })
                .setNegativeButton(R.string.btn_cancel, null)
                .show();
    }

    private void confirmClearHistory() {
        new AlertDialog.Builder(requireContext())
                .setTitle(R.string.confirm_clear_history_title)
                .setMessage(R.string.confirm_clear_history_msg)
                .setPositiveButton(R.string.btn_clear_history, (dialog, which) -> {
                    String userId = authViewModel.getCurrentUserId();
                    if (userId != null) {
                        historyViewModel.clearAllHistory(userId);
                    }
                })
                .setNegativeButton(R.string.btn_cancel, null)
                .show();
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
