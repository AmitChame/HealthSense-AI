package com.healthsenseai.ui.recommendation.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.healthsenseai.R;
import com.healthsenseai.data.model.FamilyRecommendation;
import com.healthsenseai.data.model.RecommendationCategory;
import com.healthsenseai.databinding.ItemFamilyRecommendationBinding;
import com.healthsenseai.utils.ViewUtils;
import java.util.ArrayList;
import java.util.List;

/**
 * RecyclerView Adapter for Family Member Recommendations.
 */
public class FamilyRecommendationAdapter extends RecyclerView.Adapter<FamilyRecommendationAdapter.ViewHolder> {

    private List<FamilyRecommendation> recommendations = new ArrayList<>();

    public void setRecommendations(List<FamilyRecommendation> recommendations) {
        this.recommendations = recommendations != null ? recommendations : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemFamilyRecommendationBinding binding = ItemFamilyRecommendationBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false
        );
        return new ViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        holder.bind(recommendations.get(position));
    }

    @Override
    public int getItemCount() {
        return recommendations.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        private final ItemFamilyRecommendationBinding binding;

        public ViewHolder(ItemFamilyRecommendationBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(FamilyRecommendation rec) {
            binding.tvRecMemberName.setText(rec.getFamilyMemberName());
            binding.tvRecMemberAvatar.setText(ViewUtils.getInitials(rec.getFamilyMemberName()));

            if (rec.getHealthSummary() != null && !rec.getHealthSummary().isEmpty()) {
                binding.tvRecMemberHealthSummary.setText(rec.getHealthSummary());
                binding.tvRecMemberHealthSummary.setVisibility(View.VISIBLE);
            } else {
                binding.tvRecMemberHealthSummary.setText("General Health Profile");
                binding.tvRecMemberHealthSummary.setVisibility(View.VISIBLE);
            }

            binding.tvWhyReason.setText(rec.getSummaryReason());

            // Status Styling
            RecommendationCategory category = rec.getCategory();
            String freq = rec.getFrequencyRecommendation() != null ? rec.getFrequencyRecommendation() : "";
            String riskText = freq.isEmpty() ? String.format("Risk: %s", rec.getRiskLevel() != null ? rec.getRiskLevel().getDisplayName() : "Low")
                    : String.format("Risk: %s • %s", rec.getRiskLevel() != null ? rec.getRiskLevel().getDisplayName() : "Low", freq);

            if (category == RecommendationCategory.SUITABLE) {
                binding.layoutStatusBadge.setBackgroundResource(R.drawable.bg_status_suitable);
                binding.ivStatusIcon.setImageResource(R.drawable.ic_check_circle);
                binding.ivStatusIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_suitable));
                binding.tvRecommendationStatus.setText(R.string.status_suitable_label);
                binding.tvRecommendationStatus.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_suitable_text));
                binding.tvRiskLevel.setText(riskText);
                binding.tvRiskLevel.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_suitable_text));
            } else if (category == RecommendationCategory.CAUTION) {
                binding.layoutStatusBadge.setBackgroundResource(R.drawable.bg_status_caution);
                binding.ivStatusIcon.setImageResource(R.drawable.ic_warning);
                binding.ivStatusIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_caution));
                binding.tvRecommendationStatus.setText(R.string.status_caution_label);
                binding.tvRecommendationStatus.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_caution_text));
                binding.tvRiskLevel.setText(riskText);
                binding.tvRiskLevel.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_caution_text));
            } else {
                binding.layoutStatusBadge.setBackgroundResource(R.drawable.bg_status_danger);
                binding.ivStatusIcon.setImageResource(R.drawable.ic_cancel);
                binding.ivStatusIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger));
                binding.tvRecommendationStatus.setText(R.string.status_not_recommended_label);
                binding.tvRecommendationStatus.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger_text));
                binding.tvRiskLevel.setText(riskText);
                binding.tvRiskLevel.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger_text));
            }

            // Health Factors List
            if (rec.getHealthFactors() != null && !rec.getHealthFactors().isEmpty()) {
                binding.tvFactorsHeader.setVisibility(View.VISIBLE);
                binding.rvHealthFactors.setVisibility(View.VISIBLE);

                HealthFactorAdapter factorAdapter = new HealthFactorAdapter();
                binding.rvHealthFactors.setLayoutManager(new LinearLayoutManager(binding.getRoot().getContext()));
                binding.rvHealthFactors.setAdapter(factorAdapter);
                factorAdapter.setFactors(rec.getHealthFactors());
            } else {
                binding.tvFactorsHeader.setVisibility(View.GONE);
                binding.rvHealthFactors.setVisibility(View.GONE);
            }
        }
    }
}
