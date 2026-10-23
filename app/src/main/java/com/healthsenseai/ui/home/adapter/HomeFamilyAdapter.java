package com.healthsenseai.ui.home.adapter;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.databinding.ItemFamilyMemberHorizontalBinding;
import com.healthsenseai.utils.ViewUtils;
import java.util.ArrayList;
import java.util.List;

/**
 * RecyclerView Adapter for horizontal family member cards on Home dashboard.
 */
public class HomeFamilyAdapter extends RecyclerView.Adapter<HomeFamilyAdapter.ViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(FamilyMember member);
    }

    private List<FamilyMember> members = new ArrayList<>();
    private final OnItemClickListener listener;

    public HomeFamilyAdapter(OnItemClickListener listener) {
        this.listener = listener;
    }

    public void setMembers(List<FamilyMember> newMembers) {
        this.members = newMembers != null ? newMembers : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemFamilyMemberHorizontalBinding binding = ItemFamilyMemberHorizontalBinding.inflate(
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
        private final ItemFamilyMemberHorizontalBinding binding;

        public ViewHolder(ItemFamilyMemberHorizontalBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(FamilyMember member, OnItemClickListener listener) {
            binding.tvHomeMemberName.setText(member.getName());
            binding.tvHomeMemberAvatar.setText(ViewUtils.getInitials(member.getName()));

            int conditionCount = (member.getHealthConditions() != null ? member.getHealthConditions().size() : 0)
                    + (member.getAllergies() != null ? member.getAllergies().size() : 0);

            if (conditionCount == 0) {
                binding.tvHomeMemberConditionCount.setText("No conditions");
            } else if (conditionCount == 1) {
                binding.tvHomeMemberConditionCount.setText("1 Alert");
            } else {
                binding.tvHomeMemberConditionCount.setText(conditionCount + " Alerts");
            }

            binding.getRoot().setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(member);
                }
            });
        }
    }
}
