# HealthSense AI ProGuard / R8 Rules
# Reviewed for compatibility with: Retrofit 2.11, OkHttp 4.12, Firebase BoM 33.2,
# CameraX 1.3.4, ML Kit Barcode 17.3, Material 1.12, Glide 4.16, Gson 2.11

# ─── Retrofit & OkHttp ───────────────────────────────────────────────────────
-dontwarn okhttp3.**
-dontwarn okio.**
-dontwarn retrofit2.**
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes Exceptions
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# ─── Gson Serialization ───────────────────────────────────────────────────────
# Gson uses reflection — keep all model + DTO classes to prevent stripping
-keepattributes EnclosingMethod
-keep class com.google.gson.** { *; }
-keep class com.healthsenseai.data.model.** { *; }
-keep class com.healthsenseai.data.remote.dto.** { *; }
# Keep fields with @SerializedName so Gson can deserialize API responses
-keepclassmembers class com.healthsenseai.data.model.** {
    @com.google.gson.annotations.SerializedName <fields>;
    <fields>;
}

# ─── Firebase ────────────────────────────────────────────────────────────────
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.firebase.**

# ─── ML Kit Barcode Scanning ─────────────────────────────────────────────────
-keep class com.google.mlkit.** { *; }
-dontwarn com.google.mlkit.**

# ─── CameraX ─────────────────────────────────────────────────────────────────
-keep class androidx.camera.** { *; }
-dontwarn androidx.camera.**

# ─── Glide ────────────────────────────────────────────────────────────────────
-keep public class * extends com.bumptech.glide.module.AppGlideModule
-keep class com.bumptech.glide.GeneratedAppGlideModuleImpl { *; }
-keep class * implements com.bumptech.glide.module.GlideModule
-keepclassmembers class * {
    @com.bumptech.glide.annotation.GlideOption <methods>;
    @com.bumptech.glide.annotation.GlideExtension <methods>;
}

# ─── Enums ────────────────────────────────────────────────────────────────────
# Enums with Gson @SerializedName must not be obfuscated
-keepclassmembers enum com.healthsenseai.** {
    public static **[] values();
    public static ** valueOf(java.lang.String);
    *;
}

# ─── HealthSense Utilities ────────────────────────────────────────────────────
-keep class com.healthsenseai.utils.** { *; }
-keep class com.healthsenseai.HealthSenseApp { *; }

