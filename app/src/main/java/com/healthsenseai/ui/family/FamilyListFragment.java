package com.healthsenseai.ui.family;

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
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.databinding.FragmentFamilyListBinding;
import com.healthsenseai.ui.family.adapter.FamilyMemberAdapter;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.viewmodel.AuthViewModel;
import com.healthsenseai.viewmodel.FamilyViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;

/**
 * Fragment displaying list of all registered family member profiles.
 */
public class FamilyListFragment extends Fragment {

    private FragmentFamilyListBinding binding;
    private AuthViewModel authViewModel;
    private FamilyViewModel familyViewModel;
    private FamilyMemberAdapter adapter;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        binding = FragmentFamilyListBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ViewModelFactory factory = ViewModelFactory.getInstance();
        authViewModel = new ViewModelProvider(requireActivity(), factory).get(AuthViewModel.class);
        familyViewModel = new ViewModelProvider(requireActivity(), factory).get(FamilyViewModel.class);

        setupRecyclerView();
        setupListeners();
        observeFamilyMembers();
    }

    private void setupRecyclerView() {
        adapter = new FamilyMemberAdapter(member -> {
            Intent intent = new Intent(requireContext(), FamilyMemberDetailActivity.class);
            intent.putExtra(Constants.EXTRA_FAMILY_MEMBER, member);
            startActivity(intent);
        });
        binding.rvFamilyMembers.setLayoutManager(new LinearLayoutManager(requireContext()));
        binding.rvFamilyMembers.setAdapter(adapter);
    }

    private void setupListeners() {
        binding.fabAddMember.setOnClickListener(v -> {
            Intent intent = new Intent(requireContext(), AddEditFamilyMemberActivity.class);
            startActivity(intent);
        });

        binding.btnEmptyAdd.setOnClickListener(v -> {
            Intent intent = new Intent(requireContext(), AddEditFamilyMemberActivity.class);
            startActivity(intent);
        });
    }

    private void observeFamilyMembers() {
        String userId = authViewModel.getCurrentUserId();
        if (userId != null) {
            familyViewModel.getFamilyMembers(userId).observe(getViewLifecycleOwner(), result -> {
                if (result == null) return;

                if (result.isLoading()) {
                    binding.progressFamily.setVisibility(View.VISIBLE);
                } else if (result.isSuccess()) {
                    binding.progressFamily.setVisibility(View.GONE);
                    java.util.List<FamilyMember> members = result.getData();
                    if (members != null && !members.isEmpty()) {
                        binding.rvFamilyMembers.setVisibility(View.VISIBLE);
                        binding.layoutEmptyState.setVisibility(View.GONE);
                        adapter.setMembers(members);
                    } else {
                        binding.rvFamilyMembers.setVisibility(View.GONE);
                        binding.layoutEmptyState.setVisibility(View.VISIBLE);
                    }
                } else if (result.isError()) {
                    binding.progressFamily.setVisibility(View.GONE);
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
