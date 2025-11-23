package com.thelocalshield

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.provider.Settings
import android.util.Log
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/**
 * Simple Android push notifications module
 * Uses Android ID as a unique device identifier (can be replaced with FCM later)
 */
class SimpleAndroidPushModule : Module() {
  private val TAG = "SimpleAndroidPush"
  private val CHANNEL_ID = "emergency_notifications"
  private val CHANNEL_NAME = "Emergency Notifications"

  override fun definition() = ModuleDefinition {
    Name("AndroidPushNotifications")

    OnCreate {
      createNotificationChannel()
    }

    AsyncFunction("getToken") {
      getDeviceToken()
    }

    AsyncFunction("isAvailable") {
      true
    }

    AsyncFunction("requestPermissions") {
      true
    }
  }

  private fun createNotificationChannel() {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
      val channel = NotificationChannel(
        CHANNEL_ID,
        CHANNEL_NAME,
        NotificationManager.IMPORTANCE_HIGH
      ).apply {
        description = "Emergency notifications channel"
        enableVibration(true)
        enableLights(true)
      }

      val notificationManager = appContext.reactContext?.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
      notificationManager?.createNotificationChannel(channel)
      Log.d(TAG, "Notification channel created")
    }
  }

  private suspend fun getDeviceToken(): String {
    // For now, use Android ID as device identifier
    // In production, replace with FCM token
    val androidId = Settings.Secure.getString(
      appContext.reactContext?.contentResolver,
      Settings.Secure.ANDROID_ID
    ) ?: "unknown-device"
    
    // Format as "android-{androidId}" to distinguish from Expo tokens
    val token = "android-$androidId"
    Log.d(TAG, "Device token: $token")
    return token
  }
}

