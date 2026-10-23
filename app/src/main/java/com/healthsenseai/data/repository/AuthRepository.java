package com.healthsenseai.data.repository;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.model.User;
import com.healthsenseai.utils.Constants;

/**
 * Authentication Repository handling Firebase Authentication and Firestore User profile management.
 */
public class AuthRepository {

    private final FirebaseAuth firebaseAuth;
    private final FirebaseFirestore firestore;

    public AuthRepository() {
        this.firebaseAuth = FirebaseAuth.getInstance();
        this.firestore = FirebaseFirestore.getInstance();
    }

    public boolean isUserLoggedIn() {
        return firebaseAuth.getCurrentUser() != null;
    }

    public String getCurrentUserId() {
        FirebaseUser user = firebaseAuth.getCurrentUser();
        return user != null ? user.getUid() : null;
    }

    public FirebaseUser getCurrentFirebaseUser() {
        return firebaseAuth.getCurrentUser();
    }

    public LiveData<Result<FirebaseUser>> login(String email, String password) {
        MutableLiveData<Result<FirebaseUser>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        firebaseAuth.signInWithEmailAndPassword(email, password)
                .addOnSuccessListener(authResult -> {
                    resultLiveData.setValue(Result.success(authResult.getUser()));
                })
                .addOnFailureListener(e -> {
                    String errorMsg = e.getMessage() != null ? e.getMessage() : "Authentication failed";
                    resultLiveData.setValue(Result.error(errorMsg, e));
                });

        return resultLiveData;
    }

    public LiveData<Result<User>> register(String name, String email, String password) {
        MutableLiveData<Result<User>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        firebaseAuth.createUserWithEmailAndPassword(email, password)
                .addOnSuccessListener(authResult -> {
                    FirebaseUser firebaseUser = authResult.getUser();
                    if (firebaseUser != null) {
                        String userId = firebaseUser.getUid();
                        User user = new User(userId, name, email);

                        // Save user profile document to Firestore
                        firestore.collection(Constants.COLLECTION_USERS)
                                .document(userId)
                                .set(user)
                                .addOnSuccessListener(aVoid -> {
                                    resultLiveData.setValue(Result.success(user));
                                })
                                .addOnFailureListener(e -> {
                                    // Even if Firestore doc write fails, user is authenticated; return user
                                    resultLiveData.setValue(Result.success(user));
                                });
                    } else {
                        resultLiveData.setValue(Result.error("Failed to obtain registered user details"));
                    }
                })
                .addOnFailureListener(e -> {
                    String errorMsg = e.getMessage() != null ? e.getMessage() : "Registration failed";
                    resultLiveData.setValue(Result.error(errorMsg, e));
                });

        return resultLiveData;
    }

    public LiveData<Result<Void>> sendPasswordReset(String email) {
        MutableLiveData<Result<Void>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        firebaseAuth.sendPasswordResetEmail(email)
                .addOnSuccessListener(aVoid -> {
                    resultLiveData.setValue(Result.success(null));
                })
                .addOnFailureListener(e -> {
                    String errorMsg = e.getMessage() != null ? e.getMessage() : "Failed to send password reset email";
                    resultLiveData.setValue(Result.error(errorMsg, e));
                });

        return resultLiveData;
    }

    public LiveData<Result<User>> getUserProfile(String userId) {
        MutableLiveData<Result<User>> resultLiveData = new MutableLiveData<>();
        resultLiveData.setValue(Result.loading());

        if (userId == null) {
            resultLiveData.setValue(Result.error("User ID is required"));
            return resultLiveData;
        }

        firestore.collection(Constants.COLLECTION_USERS)
                .document(userId)
                .get()
                .addOnSuccessListener(documentSnapshot -> {
                    if (documentSnapshot.exists()) {
                        User user = documentSnapshot.toObject(User.class);
                        resultLiveData.setValue(Result.success(user));
                    } else {
                        // Fallback to FirebaseUser details
                        FirebaseUser fbUser = firebaseAuth.getCurrentUser();
                        if (fbUser != null) {
                            User user = new User(userId, fbUser.getDisplayName() != null ? fbUser.getDisplayName() : "User", fbUser.getEmail());
                            resultLiveData.setValue(Result.success(user));
                        } else {
                            resultLiveData.setValue(Result.error("User profile not found"));
                        }
                    }
                })
                .addOnFailureListener(e -> {
                    resultLiveData.setValue(Result.error(e.getMessage() != null ? e.getMessage() : "Failed to load user profile", e));
                });

        return resultLiveData;
    }

    public void logout() {
        firebaseAuth.signOut();
    }
}
