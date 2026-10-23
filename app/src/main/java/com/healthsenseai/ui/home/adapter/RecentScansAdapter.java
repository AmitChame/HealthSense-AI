package com.healthsenseai.ui.home.adapter;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.healthsenseai.R;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.databinding.ItemRecentScanBinding;
import com.healthsenseai.utils.DateTimeUtils;
import java.util.ArrayList;
import java.util.List;

/**
 * RecyclerView Adapter for recent scans preview on Home dashboard.
 */
public class RecentScansAdapter extends RecyclerView.Adapter<RecentScansAdapter.ViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(ScanHistoryItem item);
    }

    private List<ScanHistoryItem> items = new ArrayList<>();
    private final OnItemClickListener listener;

    public RecentScansAdapter(OnItemClickListener listener) {
        this.listener = listener;
    }

    public void setItems(List<ScanHistoryItem> newItems) {
        this.items = newItems != null ? newItems : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemRecentScanBinding binding = ItemRecentScanBinding.inflate(
                LayoutInflater.from(parent.getContext()), parent, false
        );
        return new ViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        holder.bind(items.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return Math.min(5, items.size()); // Show top 5 on dashboard
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        private final ItemRecentScanBinding binding;

        public ViewHolder(ItemRecentScanBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(ScanHistoryItem item, OnItemClickListener listener) {
            binding.tvRecentProductName.setText(item.getProductName());

            String brand = item.getBrand() != null && !item.getBrand().isEmpty() ? " • " + item.getBrand() : "";
            binding.tvRecentScanDate.setText(DateTimeUtils.formatShortDate(item.getTimestampMillis()) + brand);

            if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
                Glide.with(binding.ivRecentScanThumb.getContext())
                        .load(item.getImageUrl())
                        .placeholder(R.drawable.ic_nutrition)
                        .error(R.drawable.ic_nutrition)
                        .centerCrop()
                        .into(binding.ivRecentScanThumb);
            } else {
                binding.ivRecentScanThumb.setImageResource(R.drawable.ic_nutrition);
            }

            binding.getRoot().setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(item);
                }
            });
        }
    }
}
