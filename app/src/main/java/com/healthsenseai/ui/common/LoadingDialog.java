package com.healthsenseai.ui.common;

import android.app.Dialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.view.LayoutInflater;
import android.view.Window;
import com.healthsenseai.databinding.DialogLoadingBinding;

/**
 * Custom non-blocking Loading Dialog.
 */
public class LoadingDialog {

    private final Dialog dialog;
    private final DialogLoadingBinding binding;

    public LoadingDialog(Context context) {
        dialog = new Dialog(context);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        binding = DialogLoadingBinding.inflate(LayoutInflater.from(context));
        dialog.setContentView(binding.getRoot());

        if (dialog.getWindow() != null) {
            dialog.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        }
        dialog.setCancelable(false);
    }

    public void show(String message) {
        if (message != null && binding.tvDialogMessage != null) {
            binding.tvDialogMessage.setText(message);
        }
        if (!dialog.isShowing()) {
            dialog.show();
        }
    }

    public void dismiss() {
        if (dialog.isShowing()) {
            dialog.dismiss();
        }
    }
}
