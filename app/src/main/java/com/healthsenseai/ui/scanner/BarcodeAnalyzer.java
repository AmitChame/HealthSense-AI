package com.healthsenseai.ui.scanner;

import android.annotation.SuppressLint;
import androidx.annotation.NonNull;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import com.google.mlkit.vision.barcode.BarcodeScanner;
import com.google.mlkit.vision.barcode.BarcodeScannerOptions;
import com.google.mlkit.vision.barcode.BarcodeScanning;
import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.common.InputImage;
import java.util.List;

/**
 * CameraX ImageAnalysis analyzer utilizing Google ML Kit Barcode Scanning.
 */
public class BarcodeAnalyzer implements ImageAnalysis.Analyzer {

    public interface OnBarcodeDetectedListener {
        void onBarcodeDetected(String barcode);
    }

    private final OnBarcodeDetectedListener listener;
    private final BarcodeScanner scanner;
    private boolean isScanningEnabled = true;

    public BarcodeAnalyzer(OnBarcodeDetectedListener listener) {
        this.listener = listener;

        // Configure scanner for all standard food product barcodes (EAN-13, EAN-8, UPC-A, UPC-E, Code 128, QR)
        BarcodeScannerOptions options = new BarcodeScannerOptions.Builder()
                .setBarcodeFormats(
                        Barcode.FORMAT_EAN_13,
                        Barcode.FORMAT_EAN_8,
                        Barcode.FORMAT_UPC_A,
                        Barcode.FORMAT_UPC_E,
                        Barcode.FORMAT_CODE_128,
                        Barcode.FORMAT_CODE_39,
                        Barcode.FORMAT_QR_CODE
                )
                .build();

        this.scanner = BarcodeScanning.getClient(options);
    }

    public void setScanningEnabled(boolean enabled) {
        this.isScanningEnabled = enabled;
    }

    @Override
    public void analyze(@NonNull ImageProxy imageProxy) {
        if (!isScanningEnabled) {
            imageProxy.close();
            return;
        }

        @SuppressLint("UnsafeOptInUsageError")
        android.media.Image mediaImage = imageProxy.getImage();
        if (mediaImage != null) {
            InputImage image = InputImage.fromMediaImage(mediaImage, imageProxy.getImageInfo().getRotationDegrees());

            scanner.process(image)
                    .addOnSuccessListener(barcodes -> {
                        if (barcodes != null && !barcodes.isEmpty() && isScanningEnabled) {
                            for (Barcode barcode : barcodes) {
                                String rawValue = barcode.getRawValue();
                                if (rawValue != null && !rawValue.trim().isEmpty()) {
                                    isScanningEnabled = false; // Stop further scans while processing
                                    if (listener != null) {
                                        listener.onBarcodeDetected(rawValue.trim());
                                    }
                                    break;
                                }
                            }
                        }
                    })
                    .addOnFailureListener(e -> {
                        // Ignore individual frame processing failures
                    })
                    .addOnCompleteListener(task -> imageProxy.close());
        } else {
            imageProxy.close();
        }
    }
}
