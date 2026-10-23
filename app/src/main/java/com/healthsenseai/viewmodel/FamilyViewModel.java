package com.healthsenseai.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.ViewModel;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.repository.FamilyRepository;
import java.util.List;

/**
 * ViewModel managing family members list and CRUD operations.
 */
public class FamilyViewModel extends ViewModel {

    private final FamilyRepository familyRepository;

    public FamilyViewModel(FamilyRepository familyRepository) {
        this.familyRepository = familyRepository;
    }

    public LiveData<Result<List<FamilyMember>>> getFamilyMembers(String userId) {
        return familyRepository.getFamilyMembers(userId);
    }

    public LiveData<Result<FamilyMember>> getFamilyMemberById(String userId, String memberId) {
        return familyRepository.getFamilyMemberById(userId, memberId);
    }

    public LiveData<Result<String>> addFamilyMember(String userId, FamilyMember member) {
        return familyRepository.addFamilyMember(userId, member);
    }

    public LiveData<Result<Void>> updateFamilyMember(String userId, FamilyMember member) {
        return familyRepository.updateFamilyMember(userId, member);
    }

    public LiveData<Result<Void>> deleteFamilyMember(String userId, String memberId) {
        return familyRepository.deleteFamilyMember(userId, memberId);
    }
}
