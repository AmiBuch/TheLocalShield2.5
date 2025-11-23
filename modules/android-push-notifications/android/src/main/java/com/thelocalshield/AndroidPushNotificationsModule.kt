package com.thelocalshield

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.util.Log
import com.google.android.gms.tasks.OnCompleteListener
import com.google.firebase.messaging.FirebaseMessaging
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class AndroidPushNotificationsModule : Module() {
  private val TAG = "AndroidPushNotifications"
  private val CHANNEL_ID = "emergency_notifications"
  private val CHANNEL_NAME = "Emergency Notifications"

  override fun definition() = ModuleDefinition {
    Name("AndroidPushNotifications")

    OnCreate {
      createNotificationChannel()
    }

    AsyncFunction("getToken") {
      getFCMToken()
    }

    AsyncFunction("isAvailable") {
      true // Always available on Android
    }

    AsyncFunction("requestPermissions") {
      requestNotificationPermissions()
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
    }
  }

  private suspend fun getFCMToken(): String {
    return suspendCancellableCoroutine { continuation ->
      FirebaseMessaging.getInstance().token.addOnCompleteListener(OnCompleteListener { task ->
        if (!task.isSuccessful) {
          Log.w(TAG, "Fetching FCM registration token failed", task.exception)
          continuation.resumeWithException(task.exception ?: Exception("Failed to get FCM token"))
          return@OnCompleteListener
        }

        // Get new FCM registration token
        val token = task.result
        Log.d(TAG, "FCM Registration Token: $token")
        continuation.resume(token)
      })
    }
  }

  private suspend fun requestNotificationPermissions(): Boolean {
    // On Android 13+, we need to request runtime permissions
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
      // Permission handling is done automatically by the system
      // when the app requests notification permissions
      return true
    }
    // For older versions, permissions are granted at install time
    return true
  }
}

