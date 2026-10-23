package com.healthsenseai.ui.recommendation.adapter;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;
import com.healthsenseai.R;
import com.healthsenseai.data.model.HealthFactor;
import com.healthsenseai.data.model.RiskLevel;
import com.healthsenseai.databinding.ItemHealthFactorBinding;
import java.util.ArrayList;
import java.util.List;

/**
 * RecyclerView Adapter for individual nutrient & allergen health factors.
 */
public class HealthFactorAdapter extends RecyclerView.Adapter<HealthFactorAdapter.ViewHolder> {

    private List<HealthFactor> factors = new ArrayList<>();

    public void setFactors(List<HealthFactor> factors) {
        this.factors = factors != null ? factors : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemHealthFactorBinding binding = ItemHealthFactorBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false
        );
        return new ViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        holder.bind(factors.get(position));
    }

    @Override
    public int getItemCount() {
        return factors.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        private final ItemHealthFactorBinding binding;

        public ViewHolder(ItemHealthFactorBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(HealthFactor factor) {
            binding.tvFactorName.setText(factor.getName());
            binding.tvFactorDesc.setText(factor.getDescription());

            if (factor.getImpact() == RiskLevel.HIGH || factor.isAllergen()) {
                binding.ivFactorIcon.setImageResource(R.drawable.ic_cancel);
                binding.ivFactorIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger));
            } else if (factor.getImpact() == RiskLevel.MODERATE) {
                binding.ivFactorIcon.setImageResource(R.drawable.ic_warning);
                binding.ivFactorIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_caution));
            } else {
                binding.ivFactorIcon.setImageResource(R.drawable.ic_check_circle);
                binding.ivFactorIcon.setColorFilter(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_suitable));
            }
        }
    }
}
