package com.healthsenseai.data.local;

import android.content.Context;
import android.content.SharedPreferences;
import com.healthsenseai.utils.Constants;

/**
 * SharedPreferences manager for local app configuration and settings.
 */
public class AppPreferences {

    private static AppPreferences instance;
    private final SharedPreferences preferences;

    private AppPreferences(Context context) {
        preferences = context.getApplicationContext().getSharedPreferences(Constants.PREF_NAME, Context.MODE_PRIVATE);
    }

    public static synchronized void init(Context context) {
        if (instance == null) {
            instance = new AppPreferences(context);
        }
    }

    public static synchronized AppPreferences getInstance() {
        if (instance == null) {
            throw new IllegalStateException("AppPreferences must be initialized in Application.onCreate()");
        }
        return instance;
    }

    public String getFastApiBaseUrl() {
        return preferences.getString(Constants.KEY_FASTAPI_URL, Constants.DEFAULT_FASTAPI_BASE_URL);
    }

    public void setFastApiBaseUrl(String url) {
        preferences.edit().putString(Constants.KEY_FASTAPI_URL, url).apply();
    }

    public boolean isOfflineMode() {
        return preferences.getBoolean(Constants.KEY_OFFLINE_MODE, false);
    }

    public void setOfflineMode(boolean offline) {
        preferences.edit().putBoolean(Constants.KEY_OFFLINE_MODE, offline).apply();
    }

    public void clear() {
        preferences.edit().clear().apply();
    }
}
