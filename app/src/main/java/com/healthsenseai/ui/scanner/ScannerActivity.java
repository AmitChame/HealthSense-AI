package com.healthsenseai.ui.scanner;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.ViewModelProvider;
import com.google.common.util.concurrent.ListenableFuture;
import com.healthsenseai.R;
import com.healthsenseai.databinding.ActivityScannerBinding;
import com.healthsenseai.ui.common.BaseActivity;
import com.healthsenseai.ui.product.ProductDetailActivity;
import com.healthsenseai.utils.Constants;
import com.healthsenseai.utils.ViewUtils;
import com.healthsenseai.viewmodel.FoodProductViewModel;
import com.healthsenseai.viewmodel.ViewModelFactory;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Dedicated Barcode Scanner Activity utilizing CameraX and Google ML Kit.
 */
public class ScannerActivity extends BaseActivity {

    private static final int PERMISSION_REQUEST_CAMERA = 101;

    private ActivityScannerBinding binding;
    private FoodProductViewModel productViewModel;
    private ExecutorService cameraExecutor;
    private ProcessCameraProvider cameraProvider;
    private Camera camera;
    private BarcodeAnalyzer barcodeAnalyzer;
    private boolean isTorchOn = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityScannerBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        productViewModel = new ViewModelProvider(this, ViewModelFactory.getInstance()).get(FoodProductViewModel.class);
        cameraExecutor = Executors.newSingleThreadExecutor();

        setupControls();
        observeProductLookup();

        if (allPermissionsGranted()) {
            startCamera();
        } else {
            requestCameraPermission();
        }
    }

    private void setupControls() {
        binding.btnScannerBack.setOnClickListener(v -> finish());

        binding.btnToggleFlash.setOnClickListener(v -> toggleTorch());

        binding.btnManualEntry.setOnClickListener(v -> showManualBarcodeDialog());

        binding.btnRequestPermission.setOnClickListener(v -> requestCameraPermission());
    }

    private boolean allPermissionsGranted() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestCameraPermission() {
        ActivityCompat.requestPermissions(
                this,
                new String[]{Manifest.permission.CAMERA},
                PERMISSION_REQUEST_CAMERA
        );
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CAMERA) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                binding.layoutPermissionDenied.setVisibility(View.GONE);
                startCamera();
            } else {
                binding.layoutPermissionDenied.setVisibility(View.VISIBLE);
            }
        }
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                cameraProvider = cameraProviderFuture.get();
                bindCameraUseCases();
            } catch (ExecutionException | InterruptedException e) {
                ViewUtils.showErrorSnackbar(binding.getRoot(), getString(R.string.err_camera_init));
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindCameraUseCases() {
        if (cameraProvider == null) return;

        // Preview use case
        Preview preview = new Preview.Builder().build();
        preview.setSurfaceProvider(binding.previewView.getSurfaceProvider());

        // Barcode Analyzer use case
        barcodeAnalyzer = new BarcodeAnalyzer(barcode -> runOnUiThread(() -> handleBarcodeDetected(barcode)));

        ImageAnalysis imageAnalysis = new ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build();
        imageAnalysis.setAnalyzer(cameraExecutor, barcodeAnalyzer);

        CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

        try {
            cameraProvider.unbindAll();
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalysis);
        } catch (Exception e) {
            ViewUtils.showErrorSnackbar(binding.getRoot(), getString(R.string.err_camera_init));
        }
    }

    private void toggleTorch() {
        if (camera != null && camera.getCameraInfo().hasFlashUnit()) {
            isTorchOn = !isTorchOn;
            camera.getCameraControl().enableTorch(isTorchOn);
            binding.btnToggleFlash.setImageResource(isTorchOn ? R.drawable.ic_flash_on : R.drawable.ic_flash_off);
        }
    }

    private void handleBarcodeDetected(String barcode) {
        if (isFinishing() || isDestroyed()) return;

        binding.tvLastScannedBarcode.setText("Detected Barcode: " + barcode);
        binding.tvLastScannedBarcode.setVisibility(View.VISIBLE);

        fetchProductDetails(barcode);
    }

    private void fetchProductDetails(String barcode) {
        binding.layoutScannerLoading.setVisibility(View.VISIBLE);
        binding.tvScannerLoadingMessage.setText(getString(R.string.msg_fetching_product));

        productViewModel.fetchProductByBarcode(barcode);
    }

    private void observeProductLookup() {
        productViewModel.getProductResult().observe(this, result -> {
            if (result == null) return;

            if (result.isLoading()) {
                binding.layoutScannerLoading.setVisibility(View.VISIBLE);
            } else if (result.isSuccess()) {
                binding.layoutScannerLoading.setVisibility(View.GONE);
                if (result.getData() != null) {
                    Intent intent = new Intent(this, ProductDetailActivity.class);
                    intent.putExtra(Constants.EXTRA_FOOD_PRODUCT, result.getData());
                    startActivity(intent);
                    finish();
                }
            } else if (result.isError()) {
                binding.layoutScannerLoading.setVisibility(View.GONE);
                showProductNotFoundDialog(result.getMessage());
            }
        });
    }

    private void showProductNotFoundDialog(String errorMessage) {
        new AlertDialog.Builder(this)
                .setTitle("Product Lookup")
                .setMessage(errorMessage != null ? errorMessage : getString(R.string.err_product_not_found))
                .setPositiveButton("Scan Another", (dialog, which) -> {
                    if (barcodeAnalyzer != null) {
                        barcodeAnalyzer.setScanningEnabled(true);
                    }
                    binding.tvLastScannedBarcode.setVisibility(View.GONE);
                })
                .setNeutralButton(R.string.btn_manual_barcode, (dialog, which) -> showManualBarcodeDialog())
                .setNegativeButton(R.string.btn_close, (dialog, which) -> finish())
                .setCancelable(false)
                .show();
    }

    private void showManualBarcodeDialog() {
        View dialogView = LayoutInflater.from(this).inflate(R.layout.dialog_manual_barcode, null);
        EditText etBarcode = dialogView.findViewById(R.id.et_manual_barcode);

        new AlertDialog.Builder(this)
                .setView(dialogView)
                .setPositiveButton(R.string.btn_submit, (dialog, which) -> {
                    String input = etBarcode.getText() != null ? etBarcode.getText().toString().trim() : "";
                    if (!input.isEmpty()) {
                        handleBarcodeDetected(input);
                    } else {
                        ViewUtils.showToast(this, "Please enter a valid barcode");
                    }
                })
                .setNegativeButton(R.string.btn_cancel, (dialog, which) -> {
                    if (barcodeAnalyzer != null) {
                        barcodeAnalyzer.setScanningEnabled(true);
                    }
                })
                .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraExecutor != null) {
            cameraExecutor.shutdown();
        }
    }
}
