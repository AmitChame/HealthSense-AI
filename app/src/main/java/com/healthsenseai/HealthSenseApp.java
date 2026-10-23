package com.healthsenseai;

import android.app.Application;
import com.healthsenseai.data.local.AppPreferences;

/**
 * HealthSenseApp — Application entry point.
 * Initializes core configurations, shared preferences, and app-wide singletons.
 */
public class HealthSenseApp extends Application {

    private static HealthSenseApp instance;

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        // Initialize AppPreferences
        AppPreferences.init(this);
    }

    public static HealthSenseApp getInstance() {
        return instance;
    }
}
