package com.healthsenseai.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;
import com.google.firebase.auth.FirebaseUser;
import com.healthsenseai.data.model.Result;
import com.healthsenseai.data.model.User;
import com.healthsenseai.data.repository.AuthRepository;

/**
 * ViewModel managing authentication state, login, registration, and user profiles.
 */
public class AuthViewModel extends ViewModel {

    private final AuthRepository authRepository;
    private final MutableLiveData<Result<FirebaseUser>> loginResult = new MutableLiveData<>();
    private final MutableLiveData<Result<User>> registerResult = new MutableLiveData<>();
    private final MutableLiveData<Result<Void>> passwordResetResult = new MutableLiveData<>();

    public AuthViewModel(AuthRepository authRepository) {
        this.authRepository = authRepository;
    }

    public boolean isUserLoggedIn() {
        return authRepository.isUserLoggedIn();
    }

    public String getCurrentUserId() {
        return authRepository.getCurrentUserId();
    }

    public FirebaseUser getCurrentFirebaseUser() {
        return authRepository.getCurrentFirebaseUser();
    }

    public LiveData<Result<FirebaseUser>> getLoginResult() {
        return loginResult;
    }

    public LiveData<Result<User>> getRegisterResult() {
        return registerResult;
    }

    public LiveData<Result<Void>> getPasswordResetResult() {
        return passwordResetResult;
    }

    public void login(String email, String password) {
        authRepository.login(email, password).observeForever(loginResult::setValue);
    }

    public void register(String name, String email, String password) {
        authRepository.register(name, email, password).observeForever(registerResult::setValue);
    }

    public void sendPasswordReset(String email) {
        authRepository.sendPasswordReset(email).observeForever(passwordResetResult::setValue);
    }

    public LiveData<Result<User>> getUserProfile(String userId) {
        return authRepository.getUserProfile(userId);
    }

    public void logout() {
        authRepository.logout();
    }
}
