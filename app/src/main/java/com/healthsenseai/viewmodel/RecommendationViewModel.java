package com.healthsenseai.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.Transformations;
import androidx.lifecycle.ViewModel;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.FoodProduct;
import com.healthsenseai.data.model.RecommendationResponse;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.repository.HistoryRepository;
import com.healthsenseai.data.repository.RecommendationRepository;
import java.util.List;

/**
 * ViewModel managing AI recommendation generation and history logging.
 *
 * Employs a reactive SwitchMap pattern to ensure that if multiple analysis requests are triggered
 * (e.g. due to rapid profile updates), only the result of the LATEST request is emitted to the UI,
 * preventing race conditions and redundant UI updates.
 */
public class RecommendationViewModel extends ViewModel {

    private final RecommendationRepository recommendationRepository;
    private final HistoryRepository historyRepository;
    
    // Trigger LiveData containing the latest analysis parameters
    private final MutableLiveData<AnalysisTrigger> analysisTrigger = new MutableLiveData<>();
    
    // The actual result LiveData, automatically updated whenever analysisTrigger changes
    private final LiveData<Result<RecommendationResponse>> recommendationResult;

    private final MutableLiveData<Result<String>> saveHistoryResult = new MutableLiveData<>();

    public RecommendationViewModel(RecommendationRepository recommendationRepository, HistoryRepository historyRepository) {
        this.recommendationRepository = recommendationRepository;
        this.historyRepository = historyRepository;
        
        // Initialize recommendationResult here to safely use recommendationRepository
        this.recommendationResult = Transformations.switchMap(analysisTrigger, trigger -> 
                recommendationRepository.getRecommendations(trigger.product, trigger.members)
        );
    }

    public LiveData<Result<RecommendationResponse>> getRecommendationResult() {
        return recommendationResult;
    }

    public LiveData<Result<String>> getSaveHistoryResult() {
        return saveHistoryResult;
    }

    /**
     * Triggers a new family health analysis for the given product.
     */
    public void analyzeFoodForFamily(FoodProduct product, List<FamilyMember> familyMembers) {
        if (product != null && familyMembers != null && !familyMembers.isEmpty()) {
            analysisTrigger.setValue(new AnalysisTrigger(product, familyMembers));
        }
    }

    public void saveToHistory(String userId, FoodProduct product, RecommendationResponse response) {
        historyRepository.saveScanHistory(userId, product, response).observeForever(saveHistoryResult::setValue);
    }

    /**
     * Internal helper to encapsulate analysis parameters.
     */
    private static class AnalysisTrigger {
        final FoodProduct product;
        final List<FamilyMember> members;

        AnalysisTrigger(FoodProduct product, List<FamilyMember> members) {
            this.product = product;
            this.members = members;
        }
    }
}
