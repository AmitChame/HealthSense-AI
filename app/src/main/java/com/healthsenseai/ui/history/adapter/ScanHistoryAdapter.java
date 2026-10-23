package com.healthsenseai.ui.history.adapter;

import android.view.LayoutInflater;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.google.android.material.chip.Chip;
import com.healthsenseai.R;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.databinding.ItemScanHistoryBinding;
import com.healthsenseai.utils.DateTimeUtils;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * RecyclerView Adapter for Scan History records.
 */
public class ScanHistoryAdapter extends RecyclerView.Adapter<ScanHistoryAdapter.ViewHolder> {

    public interface OnHistoryActionListener {
        void onItemClick(ScanHistoryItem item);
        void onDeleteClick(ScanHistoryItem item);
    }

    private List<ScanHistoryItem> items = new ArrayList<>();
    private final OnHistoryActionListener listener;

    public ScanHistoryAdapter(OnHistoryActionListener listener) {
        this.listener = listener;
    }

    public void setItems(List<ScanHistoryItem> newItems) {
        this.items = newItems != null ? newItems : new ArrayList<>();
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemScanHistoryBinding binding = ItemScanHistoryBinding.inflate(
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
        return items.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        private final ItemScanHistoryBinding binding;

        public ViewHolder(ItemScanHistoryBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }

        public void bind(ScanHistoryItem item, OnHistoryActionListener listener) {
            binding.tvHistoryProductName.setText(item.getProductName());

            String brand = item.getBrand() != null && !item.getBrand().isEmpty() ? item.getBrand() : "Packaged Food";
            String barcode = item.getBarcode() != null ? " • " + item.getBarcode() : "";
            binding.tvHistoryBrandBarcode.setText(brand + barcode);

            binding.tvHistoryDate.setText(DateTimeUtils.formatTimestamp(item.getTimestampMillis()));

            if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
                Glide.with(binding.ivHistoryThumb.getContext())
                        .load(item.getImageUrl())
                        .placeholder(R.drawable.ic_nutrition)
                        .error(R.drawable.ic_nutrition)
                        .centerCrop()
                        .into(binding.ivHistoryThumb);
            } else {
                binding.ivHistoryThumb.setImageResource(R.drawable.ic_nutrition);
            }

            // Populate Family Member Suitability Summary Chips
            binding.chipGroupHistoryFamily.removeAllViews();
            Map<String, String> memberMap = item.getMemberSuitability();
            if (memberMap != null) {
                for (Map.Entry<String, String> entry : memberMap.entrySet()) {
                    Chip chip = new Chip(binding.getRoot().getContext());
                    chip.setCheckable(false);
                    chip.setClickable(false);
                    chip.setTextSize(11f);

                    String memberName = entry.getKey();
                    String status = entry.getValue();

                    if ("SUITABLE".equalsIgnoreCase(status)) {
                        chip.setText(memberName + ": Suitable");
                        chip.setChipBackgroundColorResource(R.color.status_suitable_bg);
                        chip.setChipStrokeColorResource(R.color.status_suitable_stroke);
                        chip.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_suitable_text));
                    } else if ("CAUTION".equalsIgnoreCase(status)) {
                        chip.setText(memberName + ": Caution");
                        chip.setChipBackgroundColorResource(R.color.status_caution_bg);
                        chip.setChipStrokeColorResource(R.color.status_caution_stroke);
                        chip.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_caution_text));
                    } else {
                        chip.setText(memberName + ": Not Recommended");
                        chip.setChipBackgroundColorResource(R.color.status_danger_bg);
                        chip.setChipStrokeColorResource(R.color.status_danger_stroke);
                        chip.setTextColor(ContextCompat.getColor(binding.getRoot().getContext(), R.color.status_danger_text));
                    }
                    chip.setChipStrokeWidth(1f);
                    binding.chipGroupHistoryFamily.addView(chip);
                }
            }

            binding.btnDeleteHistoryItem.setOnClickListener(v -> {
                if (listener != null) {
                    listener.onDeleteClick(item);
                }
            });

            binding.getRoot().setOnClickListener(v -> {
                if (listener != null) {
                    listener.onItemClick(item);
                }
            });
        }
    }
}
