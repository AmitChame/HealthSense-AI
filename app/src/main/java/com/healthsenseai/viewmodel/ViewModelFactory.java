package com.healthsenseai.viewmodel;

import androidx.annotation.NonNull;
import androidx.lifecycle.ViewModel;
import androidx.lifecycle.ViewModelProvider;
import com.healthsenseai.data.repository.AuthRepository;
import com.healthsenseai.data.repository.FamilyRepository;
import com.healthsenseai.data.repository.FoodProductRepository;
import com.healthsenseai.data.repository.HistoryRepository;
import com.healthsenseai.data.repository.RecommendationRepository;

/**
 * ViewModelProvider.Factory for instantiating ViewModels with dependency-injected repositories.
 */
public class ViewModelFactory implements ViewModelProvider.Factory {

    private static ViewModelFactory instance;

    private final AuthRepository authRepository;
    private final FamilyRepository familyRepository;
    private final FoodProductRepository foodProductRepository;
    private final RecommendationRepository recommendationRepository;
    private final HistoryRepository historyRepository;

    public ViewModelFactory() {
        this.authRepository = new AuthRepository();
        this.familyRepository = new FamilyRepository();
        this.foodProductRepository = new FoodProductRepository();
        this.recommendationRepository = new RecommendationRepository();
        this.historyRepository = new HistoryRepository();
    }

    public static synchronized ViewModelFactory getInstance() {
        if (instance == null) {
            instance = new ViewModelFactory();
        }
        return instance;
    }

    @NonNull
    @Override
    @SuppressWarnings("unchecked")
    public <T extends ViewModel> T create(@NonNull Class<T> modelClass) {
        if (modelClass.isAssignableFrom(AuthViewModel.class)) {
            return (T) new AuthViewModel(authRepository);
        } else if (modelClass.isAssignableFrom(FamilyViewModel.class)) {
            return (T) new FamilyViewModel(familyRepository);
        } else if (modelClass.isAssignableFrom(FoodProductViewModel.class)) {
            return (T) new FoodProductViewModel(foodProductRepository);
        } else if (modelClass.isAssignableFrom(RecommendationViewModel.class)) {
            return (T) new RecommendationViewModel(recommendationRepository, historyRepository);
        } else if (modelClass.isAssignableFrom(HistoryViewModel.class)) {
            return (T) new HistoryViewModel(historyRepository);
        }
        throw new IllegalArgumentException("Unknown ViewModel class: " + modelClass.getName());
    }
}
