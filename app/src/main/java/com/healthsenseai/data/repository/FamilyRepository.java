package com.healthsenseai.data.repository;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import com.google.firebase.firestore.CollectionReference;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.Query;
import com.healthsenseai.data.model.FamilyMember;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.utils.Constants;
import java.util.ArrayList;
import java.util.List;

/**
 * Repository for CRUD operations on family member health profiles.
 * Scoped to authenticated user in Firestore: users/{userId}/familyMembers/{memberId}.
 */
public class FamilyRepository {

    private final FirebaseFirestore firestore;

    public FamilyRepository() {
        this.firestore = FirebaseFirestore.getInstance();
    }

    private CollectionReference getFamilyMembersCollection(String userId) {
        return firestore.collection(Constants.COLLECTION_USERS)
                .document(userId)
                .collection(Constants.COLLECTION_FAMILY_MEMBERS);
    }

    public LiveData<Result<List<FamilyMember>>> getFamilyMembers(String userId) {
        MutableLiveData<Result<List<FamilyMember>>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || userId.trim().isEmpty()) {
            resultLiveData.setValue(Result.error("User is not authenticated"));
            return resultLiveData;
        }

        getFamilyMembersCollection(userId)
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .addSnapshotListener((querySnapshot, error) -> {
                    if (error != null) {
                        resultLiveData.setValue(Result.error(error.getMessage() != null ? error.getMessage() : "Failed to load family members", error));
                        return;
                    }

                    List<FamilyMember> members = new ArrayList<>();
                    if (querySnapshot != null) {
                        for (com.google.firebase.firestore.DocumentSnapshot doc : querySnapshot.getDocuments()) {
                            FamilyMember member = doc.toObject(FamilyMember.class);
                            if (member != null) {
                                member.setId(doc.getId());
                                member.setUserId(userId);
                                members.add(member);
                            }
                        }
                    }
                    resultLiveData.setValue(Result.success(members));
                });

        return resultLiveData;
    }

    public LiveData<Result<FamilyMember>> getFamilyMemberById(String userId, String memberId) {
        MutableLiveData<Result<FamilyMember>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || memberId == null) {
            resultLiveData.setValue(Result.error("Invalid parameters"));
            return resultLiveData;
        }

        getFamilyMembersCollection(userId)
                .document(memberId)
                .get()
                .addOnSuccessListener(doc -> {
                    if (doc.exists()) {
                        FamilyMember member = doc.toObject(FamilyMember.class);
                        if (member != null) {
                            member.setId(doc.getId());
                            member.setUserId(userId);
                            resultLiveData.setValue(Result.success(member));
                        } else {
                            resultLiveData.setValue(Result.error("Failed to parse member profile"));
                        }
                    } else {
                        resultLiveData.setValue(Result.error("Family member profile not found"));
                    }
                })
                .addOnFailureListener(e -> {
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to fetch family member", e));
                });

        return resultLiveData;
    }

    public LiveData<Result<String>> addFamilyMember(String userId, FamilyMember member) {
        MutableLiveData<Result<String>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null) {
            resultLiveData.setValue(Result.error("User is not authenticated"));
            return resultLiveData;
        }

        member.setUserId(userId);
        DocumentReference newDocRef = getFamilyMembersCollection(userId).document();
        member.setId(newDocRef.getId());

        newDocRef.set(member)
                .addOnSuccessListener(aVoid -> {
                    resultLiveData.setValue(Result.success(newDocRef.getId()));
                })
                .addOnFailureListener(e -> {
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to add family member", e));
                });

        return resultLiveData;
    }

    public LiveData<Result<Void>> updateFamilyMember(String userId, FamilyMember member) {
        MutableLiveData<Result<Void>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || member.getId() == null) {
            resultLiveData.setValue(Result.error("Invalid member reference"));
            return resultLiveData;
        }

        getFamilyMembersCollection(userId)
                .document(member.getId())
                .set(member)
                .addOnSuccessListener(aVoid -> {
                    resultLiveData.setValue(Result.success(null));
                })
                .addOnFailureListener(e -> {
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to update profile", e));
                });

        return resultLiveData;
    }

    public LiveData<Result<Void>> deleteFamilyMember(String userId, String memberId) {
        MutableLiveData<Result<Void>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null || memberId == null) {
            resultLiveData.setValue(Result.error("Invalid member reference"));
            return resultLiveData;
        }

        getFamilyMembersCollection(userId)
                .document(memberId)
                .delete()
                .addOnSuccessListener(aVoid -> {
                    resultLiveData.setValue(Result.success(null));
                })
                .addOnFailureListener(e -> {
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to delete profile", e));
                });

        return resultLiveData;
    }
}
