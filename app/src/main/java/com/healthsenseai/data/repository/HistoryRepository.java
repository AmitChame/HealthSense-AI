package com.healthsenseai.data.repository;

import android.util.Log;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import com.google.firebase.firestore.CollectionReference;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.Query;
import com.google.firebase.firestore.WriteBatch;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.utils.Constants;
import java.util.ArrayList;
import java.util.List;

/**
 * Repository for managing scan history records in Firestore collection:
 * users/{userId}/scanHistory/{scanId}.
 */
public class HistoryRepository {

    private static final String TAG = "HistoryRepository";
    private final FirebaseFirestore firestore;

    public HistoryRepository() {
        this.firestore = FirebaseFirestore.getInstance();
    }

    private CollectionReference getHistoryCollection(String userId) {
        return firestore.collection(Constants.COLLECTION_USERS)
                .document(userId)
                .collection(Constants.COLLECTION_SCAN_HISTORY);
    }

    public LiveData<Result<List<ScanHistoryItem>>> getScanHistory(String userId) {
        MutableLiveData<Result<List<ScanHistoryItem>>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || userId.trim().isEmpty()) {
            Log.e(TAG, "getScanHistory: User ID is null");
            resultLiveData.setValue(Result.error("User is not authenticated"));
            return resultLiveData;
        }

        getHistoryCollection(userId)
                .orderBy("timestampMillis", Query.Direction.DESCENDING)
                .addSnapshotListener((querySnapshot, error) -> {
                    if (error != null) {
                        Log.e(TAG, "getScanHistory: Firestore error", error);
                        resultLiveData.setValue(Result.error(error.getMessage() != null ? error.getMessage() : "Failed to load scan history", error));
                        return;
                    }

                    List<ScanHistoryItem> historyList = new ArrayList<>();
                    if (querySnapshot != null) {
                        for (com.google.firebase.firestore.DocumentSnapshot doc : querySnapshot.getDocuments()) {
                            ScanHistoryItem item = doc.toObject(ScanHistoryItem.class);
                            if (item != null) {
                                item.setId(doc.getId());
                                item.setUserId(userId);
                                historyList.add(item);
                            }
                        }
                        Log.d(TAG, "getScanHistory: Successfully retrieved " + historyList.size() + " items for user " + userId);
                    }
                    resultLiveData.setValue(Result.success(historyList));
                });

        return resultLiveData;
    }

    public LiveData<Result<String>> saveScanHistory(String userId, FoodProduct product, RecommendationResponse response) {
        MutableLiveData<Result<String>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null) {
            Log.e(TAG, "saveScanHistory: User ID is null");
            resultLiveData.setValue(Result.error("User is not authenticated"));
            return resultLiveData;
        }

        ScanHistoryItem item = new ScanHistoryItem(userId, product, response);
        DocumentReference docRef = getHistoryCollection(userId).document();
        item.setId(docRef.getId());

        Log.d(TAG, "saveScanHistory: Attempting to save scan for " + (product != null ? product.getProductName() : "Unknown"));

        docRef.set(item)
                .addOnSuccessListener(aVoid -> {
                    Log.d(TAG, "saveScanHistory: Successfully saved scan with ID: " + docRef.getId());
                    resultLiveData.setValue(Result.success(docRef.getId()));
                })
                .addOnFailureListener(e -> {
                    Log.e(TAG, "saveScanHistory: Failed to save scan", e);
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to save scan history", e));
                });

        return resultLiveData;
    }

    public LiveData<Result<Void>> deleteScanHistoryItem(String userId, String scanId) {
        MutableLiveData<Result<Void>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || scanId == null) {
            Log.e(TAG, "deleteScanHistoryItem: Invalid parameters");
            resultLiveData.setValue(Result.error("Invalid parameters"));
            return resultLiveData;
        }

        getHistoryCollection(userId)
                .document(scanId)
                .delete()
                .addOnSuccessListener(aVoid -> {
                    Log.d(TAG, "deleteScanHistoryItem: Successfully deleted scan: " + scanId);
                    resultLiveData.setValue(Result.success(null));
                })
                .addOnFailureListener(e -> {
                    Log.e(TAG, "deleteScanHistoryItem: Failed to delete scan: " + scanId, e);
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to delete history item", e));
                });

        return resultLiveData;
    }

    public LiveData<Result<Void>> clearAllHistory(String userId) {
        MutableLiveData<Result<Void>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null) {
            Log.e(TAG, "clearAllHistory: User ID is null");
            resultLiveData.setValue(Result.error("User is not authenticated"));
            return resultLiveData;
        }

        Log.d(TAG, "clearAllHistory: Attempting to clear all history for user: " + userId);

        getHistoryCollection(userId)
                .get()
                .addOnSuccessListener(querySnapshot -> {
                    if (querySnapshot == null || querySnapshot.isEmpty()) {
                        Log.d(TAG, "clearAllHistory: History is already empty");
                        resultLiveData.setValue(Result.success(null));
                        return;
                    }

                    WriteBatch batch = firestore.batch();
                    for (com.google.firebase.firestore.DocumentSnapshot doc : querySnapshot.getDocuments()) {
                        batch.delete(doc.getReference());
                    }
                    batch.commit()
                            .addOnSuccessListener(aVoid -> {
                                Log.d(TAG, "clearAllHistory: Successfully cleared all history");
                                resultLiveData.setValue(Result.success(null));
                            })
                            .addOnFailureListener(e -> {
                                Log.e(TAG, "clearAllHistory: Failed to commit batch clear", e);
                                resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to clear history", e));
                            });
                })
                .addOnFailureListener(e -> {
                    Log.e(TAG, "clearAllHistory: Failed to retrieve history items for clearing", e);
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to retrieve history items", e));
                });

        return resultLiveData;
    }
}
