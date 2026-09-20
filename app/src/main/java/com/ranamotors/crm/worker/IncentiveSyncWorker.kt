package com.ranamotors.crm.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.ranamotors.crm.data.local.CrmDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class IncentiveSyncWorker(
    context: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(context, workerParams) {

    private val db = CrmDatabase.getInstance(context)

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val unsyncedBookings = db.crmDao().getUnsyncedBookings()
            val unsyncedCalls = db.crmDao().getUnsyncedCallLogs()

            if (unsyncedBookings.isEmpty() && unsyncedCalls.isEmpty()) {
                return@withContext Result.success()
            }

            val payload = JSONObject().apply {
                put("timestamp", System.currentTimeMillis())
                put("bookings", JSONArray().apply {
                    unsyncedBookings.forEach { b ->
                        put(JSONObject().apply {
                            put("bookingId", b.bookingId)
                            put("customerPhoneNormalized", b.customerPhoneNormalized)
                            put("outletCode", b.outletCode)
                            put("consigneeCode", b.consigneeCode)
                            put("totalAccessoriesRetail", b.totalAccessoriesRetail)
                            put("workshopAccessoriesRetail", b.workshopAccessoriesRetail)
                            put("isBulkVehicle", b.isBulkVehicle)
                            put("isAmbulance", b.isAmbulance)
                        })
                    }
                })
                put("callLogs", JSONArray().apply {
                    unsyncedCalls.forEach { c ->
                        put(JSONObject().apply {
                            put("callEventId", c.callEventId)
                            put("bookingId", c.bookingId)
                            put("duration", c.callLogDurationSeconds)
                            put("verified", c.isSystemVerified)
                        })
                    }
                })
            }

            val url = URL("https://script.google.com/macros/s/YOUR_EXEC_ID/exec")
            val connection = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("Content-Type", "application/json")
                doOutput = true
                connectTimeout = 10000
                readTimeout = 10000
            }

            OutputStreamWriter(connection.outputStream).use { writer ->
                writer.write(payload.toString())
            }

            if (connection.responseCode == HttpURLConnection.HTTP_OK) {
                db.crmDao().markBookingsSynced(unsyncedBookings.map { it.bookingId })
                db.crmDao().markCallLogsSynced(unsyncedCalls.map { it.callEventId })
                Result.success()
            } else {
                Result.retry()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }
}
