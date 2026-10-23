package com.healthsenseai.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.ViewModel;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.model.ScanHistoryItem;
import com.healthsenseai.data.repository.HistoryRepository;
import java.util.List;

/**
 * ViewModel managing scan history viewing, filtering, and deletion.
 */
public class HistoryViewModel extends ViewModel {

    private final HistoryRepository historyRepository;

    public HistoryViewModel(HistoryRepository historyRepository) {
        this.historyRepository = historyRepository;
    }

    public LiveData<Result<List<ScanHistoryItem>>> getScanHistory(String userId) {
        return historyRepository.getScanHistory(userId);
    }

    public LiveData<Result<Void>> deleteHistoryItem(String userId, String scanId) {
        return historyRepository.deleteScanHistoryItem(userId, scanId);
    }

    public LiveData<Result<Void>> clearAllHistory(String userId) {
        return historyRepository.clearAllHistory(userId);
    }
}
