package com.ranamotors.crm.telephony

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.provider.CallLog
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class CallLogReconciler(private val context: Context) {

    suspend fun verifyCallDuration(
        targetNumber: String,
        callInitiatedTimestamp: Long
    ): Int = withContext(Dispatchers.IO) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) 
            != PackageManager.PERMISSION_GRANTED) {
            return@withContext 0
        }

        var verifiedDuration = 0
        val projection = arrayOf(
            CallLog.Calls.NUMBER,
            CallLog.Calls.NORMALIZED_NUMBER,
            CallLog.Calls.TYPE,
            CallLog.Calls.DATE,
            CallLog.Calls.DURATION
        )

        val selection = "${CallLog.Calls.DATE} >= ?"
        val selectionArgs = arrayOf((callInitiatedTimestamp - 5000).toString())
        val sortOrder = "${CallLog.Calls.DATE} DESC"

        context.contentResolver.query(
            CallLog.Calls.CONTENT_URI,
            projection, selection, selectionArgs, sortOrder
        )?.use { cursor ->
            val numberIndex = cursor.getColumnIndex(CallLog.Calls.NUMBER)
            val normalizedIndex = cursor.getColumnIndex(CallLog.Calls.NORMALIZED_NUMBER)
            val typeIndex = cursor.getColumnIndex(CallLog.Calls.TYPE)
            val durationIndex = cursor.getColumnIndex(CallLog.Calls.DURATION)

            while (cursor.moveToNext()) {
                val callType = cursor.getInt(typeIndex)
                if (callType != CallLog.Calls.OUTGOING_TYPE) continue

                val loggedNumber = cursor.getString(numberIndex) ?: ""
                val loggedNormalized = if (normalizedIndex >= 0) cursor.getString(normalizedIndex) else null

                val cleanTarget = targetNumber.replace(Regex("[^0-9]"), "")
                val cleanLogged = (loggedNormalized ?: loggedNumber).replace(Regex("[^0-9]"), "")

                if (cleanLogged.length >= 10 && cleanTarget.length >= 10 &&
                    cleanLogged.takeLast(10) == cleanTarget.takeLast(10)) {
                    verifiedDuration = cursor.getInt(durationIndex)
                    break
                }
            }
        }
        return@withContext verifiedDuration
    }
}
