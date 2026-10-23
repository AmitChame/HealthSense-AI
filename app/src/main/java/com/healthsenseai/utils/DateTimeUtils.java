package com.healthsenseai.utils;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Utility for formatting timestamps into user-friendly strings.
 */
public final class DateTimeUtils {

    private DateTimeUtils() {
        // Prevent instantiation
    }

    private static final SimpleDateFormat DISPLAY_FORMAT =
            new SimpleDateFormat("MMM d, yyyy • h:mm a", Locale.getDefault());

    private static final SimpleDateFormat SHORT_FORMAT =
            new SimpleDateFormat("MMM d, yyyy", Locale.getDefault());

    public static String formatTimestamp(long timestampMillis) {
        if (timestampMillis <= 0) {
            return "Just now";
        }
        return DISPLAY_FORMAT.format(new Date(timestampMillis));
    }

    public static String formatShortDate(long timestampMillis) {
        if (timestampMillis <= 0) {
            return "Today";
        }
        return SHORT_FORMAT.format(new Date(timestampMillis));
    }
}
