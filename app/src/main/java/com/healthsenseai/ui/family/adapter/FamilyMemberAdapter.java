package com.healthsenseai.ui.family.adapter;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;
import com.google.android.material.chip.Chip;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.databinding.ItemFamilyMemberBinding;
import com.healthsenseai.utils.ViewUtils;
import java.util.ArrayList;
import java.util.List;

/**
 * RecyclerView Adapter for Family Member List screen.
 */
public class FamilyMemberAdapter extends RecyclerView.Adapter<FamilyMemberAdapter.ViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(FamilyMember member);
    }

    private List<FamilyMember> members = new ArrayList<>();
    private final OnItemClickListener listener;

    public FamilyMemberAdapter(OnItemClickListener listener) {
        this.listener = listener;
    }

    public void setMembers(List<FamilyMember> newMembers) {
        this.members = newMembers != null ? newMembers : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemFamilyMemberBinding binding = ItemFamilyMemberBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false
        );
        return new ViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        holder.bind(members.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return members.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        private final ItemFamilyMemberBinding binding;

        public ViewHolder(ItemFamilyMemberBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(FamilyMember member, OnItemClickListener listener) {
            binding.tvItemName.setText(member.getName());
            binding.tvItemAvatar.setText(ViewUtils.getInitials(member.getName()));

            String gender = member.getGender() != null ? member.getGender() : "Not specified";
            binding.tvItemAgeGender.setText(member.getAge() + " yrs • " + gender);

            // Populate preview chips
            binding.chipGroupSummary.removeAllViews();

            // Add Health Condition Chips
            if (member.getHealthConditions() != null) {
                for (String cond : member.getHealthConditions()) {
                    if (cond == null || cond.equalsIgnoreCase("None")) continue;
                    Chip chip = new Chip(binding.getRoot().getContext());
                    chip.setText(cond);
                    chip.setCheckable(false);
                    chip.setClickable(false);
                    chip.setChipBackgroundColorResource(R.color.surface_variant);
                    chip.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.text_primary));
                    chip.setTextSize(11f);
                    binding.chipGroupSummary.addView(chip);
                }
            }

            // Add Allergy Chips (Highlighted)
            if (member.getAllergies() != null) {
                for (String allergy : member.getAllergies()) {
                    if (allergy == null || allergy.equalsIgnoreCase("None")) continue;
                    Chip chip = new Chip(binding.getRoot().getContext());
                    chip.setText("⚠️ " + allergy);
                    chip.setCheckable(false);
                    chip.setClickable(false);
                    chip.setChipBackgroundColorResource(R.color.status_danger_bg);
                    chip.setChipStrokeColorResource(R.color.status_danger_stroke);
                    chip.setChipStrokeWidth(1f);
                    chip.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger_text));
                    chip.setTextSize(11f);
                    binding.chipGroupSummary.addView(chip);
                }
            }

            binding.getRoot().setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(member);
                }
            });
        }
    }
}
