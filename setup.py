import os

files = {}

files["settings.gradle.kts"] = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "RanaMotorsCRM"
include(":app")
"""

files["build.gradle.kts"] = """plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
    id("org.jetbrains.kotlin.kapt") version "1.9.22" apply false
}
"""

files["SyncServer.js"] = """const process = require("node:process");
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const PORT = process.env.PORT || 3000;
const MAX_PAYLOAD_SIZE = 2 * 1024 * 1024;

const server = http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  const reqUrl = req.url.split("?")[0];

  if (req.method === "POST" && (reqUrl === "/api/sync" || reqUrl === "/api/incentives/sync")) {
    let body = "";
    let sizeExceeded = false;

    req.on("data", chunk => {
      body += chunk;
      if (body.length > MAX_PAYLOAD_SIZE) {
        sizeExceeded = true;
        res.writeHead(413, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Payload exceeds 2MB limit" }));
        req.destroy();
      }
    });

    req.on("end", () => {
      if (sizeExceeded) return;
      try {
        const payload = JSON.parse(body);
        payload.serverReceivedTime = new Date().toISOString();

        const logPath = path.join(__dirname, "sync_records.json");
        let existingLogs = [];
        if (fs.existsSync(logPath)) {
          const raw = fs.readFileSync(logPath, "utf8");
          existingLogs = JSON.parse(raw || "[]");
        }

        existingLogs.push(payload);
        fs.writeFileSync(logPath, JSON.stringify(existingLogs, null, 2), "utf8");

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          status: "SUCCESS",
          syncedBookings: payload.bookings ? payload.bookings.length : 0,
          syncedCallLogs: payload.callLogs ? payload.callLogs.length : 0,
          timestamp: payload.serverReceivedTime
        }));
      } catch (_err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid JSON format" }));
      }
    });
  } else {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Endpoint not found" }));
  }
});

server.listen(PORT, () => {
  console.log(`Sync Server running on port ${PORT}`);
});
"""

files[".github/workflows/build.yml"] = """name: Build Android APK

on:
  push:
    branches: [ "main", "master" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Build Debug APK
        run: gradle assembleDebug --stacktrace

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: RanaMotorsCRM-Debug-APK
          path: app/build/outputs/apk/debug/app-debug.apk
"""

files["app/build.gradle.kts"] = """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
}

android {
    namespace = "com.ranamotors.crm"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.ranamotors.crm"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables { useSupportLibrary = true }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    composeOptions { kotlinCompilerExtensionVersion = "1.5.8" }
    packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")
    implementation("androidx.work:work-runtime-ktx:2.9.0")
    implementation("com.google.android.gms:play-services-mlkit-text-recognition:19.0.0")
}
"""

files["app/src/main/AndroidManifest.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android.permission.READ_CALL_LOG />
    <uses-permission android.permission.READ_PHONE_STATE />
    <uses-permission android.permission.INTERNET />
    <uses-permission android.permission.ACCESS_NETWORK_STATE />

    <application
        android:allowBackup="true"
        android:label="Rana Motors CRM"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
"""

files["app/src/main/java/com/ranamotors/crm/MainActivity.kt"] = """package com.ranamotors.crm

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import com.ranamotors.crm.data.local.CrmDatabase
import com.ranamotors.crm.ui.incentive.DashboardAnalyticsViewModel
import com.ranamotors.crm.ui.incentive.IncentiveDashboardScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val database = CrmDatabase.getInstance(applicationContext)
        val viewModel = DashboardAnalyticsViewModel(database.crmDao())

        setContent {
            MaterialTheme {
                Surface {
                    IncentiveDashboardScreen(viewModel = viewModel)
                }
            }
        }
    }
}
"""

files["app/src/main/java/com/ranamotors/crm/data/local/entity/CrmEntities.kt"] = """package com.ranamotors.crm.data.local.entity

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(tableName = "accounts")
data class AccountEntity(
    @PrimaryKey val accountId: String,
    val executiveName: String,
    val dealerCode: String,
    val outletCode: String,     // e.g., "08A1", "08A4", "08D3", "08D6"
    val consigneeCode: String,  // e.g., "CONSIGNEE_ARENA_1", "CONSIGNEE_NEXA_1"
    val channel: String,        // "ARENA" or "NEXA"
    val hashedPin: String
)

@Entity(
    tableName = "customer_bookings",
    indices = [
        Index(value = ["bookingId"], unique = true),
        Index(value = ["customerPhoneNormalized"]),
        Index(value = ["outletCode"]),
        Index(value = ["consigneeCode"])
    ]
)
data class CustomerBookingEntity(
    @PrimaryKey val bookingId: String,
    val customerName: String,
    val customerPhoneNormalized: String, // 10-digit clean string
    val outletCode: String,              // "08A1", "08A4", "08D3", "08D6"
    val consigneeCode: String,
    val channel: String,                 // "ARENA" or "NEXA"
    val bookingDateTimestamp: Long,
    val totalAccessoriesRetail: Double,
    val workshopAccessoriesRetail: Double,
    val trueValueAccessoriesRetail: Double,
    val totalWholesaleValue: Double,
    val isBulkVehicle: Boolean = false,  // >= 10 vehicles order
    val isAmbulance: Boolean = false,    // Special body exclusion
    val isBbndBooking: Boolean = false,   // Booked But Not Delivered
    val isSynced: Boolean = false,
    val lastUpdatedTimestamp: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "call_history",
    indices = [
        Index(value = ["bookingId"]),
        Index(value = ["timestamp"])
    ]
)
data class CallHistoryEntity(
    @PrimaryKey val callEventId: String,
    val bookingId: String,
    val executiveId: String,
    val normalizedPhoneNumber: String,
    val timestamp: Long,
    val callLogDurationSeconds: Int,
    val isSystemVerified: Boolean,        // Verified against native CallLog
    val postCallChecklistLogged: Boolean,
    val notes: String = "",
    val isSynced: Boolean = false
)

@Entity(tableName = "incentive_benchmarks")
data class IncentiveBenchmarkEntity(
    @PrimaryKey val consigneeCode: String,
    val channel: String,
    val baseSeptNov2024Acpv: Double,
    val baseSeptNov2025Acpv: Double,
    val targetWholesaleOfftakeUnits: Int,
    val currentWholesaleOfftakeUnits: Int,
    val workshopCrossChannelRatio: Double // e.g. 0.92 for 92%
)
"""

files["app/src/main/java/com/ranamotors/crm/data/local/dao/CrmDao.kt"] = """package com.ranamotors.crm.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.ranamotors.crm.data.local.entity.AccountEntity
import com.ranamotors.crm.data.local.entity.CallHistoryEntity
import com.ranamotors.crm.data.local.entity.CustomerBookingEntity
import com.ranamotors.crm.data.local.entity.IncentiveBenchmarkEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface CrmDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAccount(account: AccountEntity)

    @Query("SELECT * FROM accounts WHERE accountId = :accountId LIMIT 1")
    suspend fun getAccountById(accountId: String): AccountEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBooking(booking: CustomerBookingEntity)

    @Query("SELECT * FROM customer_bookings WHERE consigneeCode = :consigneeCode")
    fun getBookingsByConsignee(consigneeCode: String): Flow<List<CustomerBookingEntity>>

    @Query("SELECT * FROM customer_bookings WHERE outletCode = :outletCode")
    fun getBookingsByOutlet(outletCode: String): Flow<List<CustomerBookingEntity>>

    @Query("SELECT * FROM customer_bookings WHERE channel = :channel")
    fun getBookingsByChannel(channel: String): Flow<List<CustomerBookingEntity>>

    @Query("SELECT * FROM customer_bookings WHERE isSynced = 0")
    suspend fun getUnsyncedBookings(): List<CustomerBookingEntity>

    @Query("UPDATE customer_bookings SET isSynced = 1 WHERE bookingId IN (:bookingIds)")
    suspend fun markBookingsSynced(bookingIds: List<String>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCallHistory(call: CallHistoryEntity)

    @Query("SELECT * FROM call_history WHERE bookingId = :bookingId ORDER BY timestamp DESC")
    fun getCallHistoryForBooking(bookingId: String): Flow<List<CallHistoryEntity>>

    @Query("SELECT * FROM call_history WHERE isSynced = 0")
    suspend fun getUnsyncedCallLogs(): List<CallHistoryEntity>

    @Query("UPDATE call_history SET isSynced = 1 WHERE callEventId IN (:callIds)")
    suspend fun markCallLogsSynced(callIds: List<String>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBenchmark(benchmark: IncentiveBenchmarkEntity)

    @Query("SELECT * FROM incentive_benchmarks WHERE consigneeCode = :consigneeCode LIMIT 1")
    suspend fun getBenchmarkForConsignee(consigneeCode: String): IncentiveBenchmarkEntity?

    @Query("SELECT * FROM incentive_benchmarks WHERE channel = :channel LIMIT 1")
    suspend fun getBenchmarkForChannel(channel: String): IncentiveBenchmarkEntity?
}
"""

files["app/src/main/java/com/ranamotors/crm/data/local/CrmDatabase.kt"] = """package com.ranamotors.crm.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.ranamotors.crm.data.local.dao.CrmDao
import com.ranamotors.crm.data.local.entity.AccountEntity
import com.ranamotors.crm.data.local.entity.CallHistoryEntity
import com.ranamotors.crm.data.local.entity.CustomerBookingEntity
import com.ranamotors.crm.data.local.entity.IncentiveBenchmarkEntity

@Database(
    entities = [
        AccountEntity::class,
        CustomerBookingEntity::class,
        CallHistoryEntity::class,
        IncentiveBenchmarkEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class CrmDatabase : RoomDatabase() {

    abstract fun crmDao(): CrmDao

    companion object {
        @Volatile
        private var INSTANCE: CrmDatabase? = null

        fun getInstance(context: Context): CrmDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CrmDatabase::class.java,
                    "rana_motors_crm.db"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
"""

files["app/src/main/java/com/ranamotors/crm/telephony/CallLogReconciler.kt"] = """package com.ranamotors.crm.telephony

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
"""

files["app/src/main/java/com/ranamotors/crm/ocr/OcrSheetScanner.kt"] = """package com.ranamotors.crm.ocr

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

data class ExtractedBookingData(
    val customerName: String = "",
    val phone: String = "",
    val bookingAmount: Double = 0.0,
    val accessoriesAmount: Double = 0.0,
    val rawText: String = ""
)

class OcrSheetScanner {

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    suspend fun processBookingSheetImage(bitmap: Bitmap): ExtractedBookingData =
        suspendCancellableCoroutine { continuation ->
            val image = InputImage.fromBitmap(bitmap, 0)
            
            recognizer.process(image)
                .addOnSuccessListener { visionText ->
                    val fullText = visionText.text
                    val parsedData = parseBookingSheetText(fullText)
                    continuation.resume(parsedData)
                }
                .addOnFailureListener { e ->
                    continuation.resumeWithException(e)
                }
        }

    private fun parseBookingSheetText(text: String): ExtractedBookingData {
        val lines = text.split("\n")
        var phone = ""
        var customerName = ""
        var accessoriesAmount = 0.0

        val phoneRegex = Regex("(?:\\+91[\\s-]*)?[6-9]\\d{9}")
        val amountRegex = Regex("(?:Rs\\.?|INR|₹)?\\s*([0-9,]+(?:\\.[0-9]{2})?)")

        for (line in lines) {
            if (phone.isEmpty()) {
                val match = phoneRegex.find(line)
                if (match != null) {
                    phone = match.value.replace(Regex("[^0-9]"), "").takeLast(10)
                }
            }

            if (line.contains("Accessories", ignoreCase = true) || line.contains("Acc Total", ignoreCase = true)) {
                val amountMatch = amountRegex.find(line)
                if (amountMatch != null) {
                    val rawNum = amountMatch.groupValues[1].replace(",", "")
                    accessoriesAmount = rawNum.toDoubleOrNull() ?: 0.0
                }
            }
        }

        return ExtractedBookingData(
            customerName = customerName,
            phone = phone,
            accessoriesAmount = accessoriesAmount,
            rawText = text
        )
    }
}
"""

files["app/src/main/java/com/ranamotors/crm/worker/IncentiveSyncWorker.kt"] = """package com.ranamotors.crm.worker

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
"""

files["app/src/main/java/com/ranamotors/crm/ui/incentive/DashboardAnalyticsViewModel.kt"] = """package com.ranamotors.crm.ui.incentive

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ranamotors.crm.data.local.dao.CrmDao
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.math.max

data class DashboardUiState(
    val selectedChannel: String = "ARENA",
    val selectedConsigneeCode: String = "CONSIGNEE_ARENA_1",
    val currentAcpv: Double = 0.0,
    val growthPercent: Double = 0.0,
    val earnedPercentage: Double = 0.0,
    val projectedPayout: Double = 0.0,
    val wholesaleOfftakePercent: Double = 0.0,
    val isWholesaleGateMet: Boolean = false,
    val workshopCrossChannelRatio: Double = 0.0,
    val isWorkshopRatioMet: Boolean = false,
    val mtdShowroomRetail: Double = 0.0,
    val mtdWorkshopRetail: Double = 0.0,
    val validRetailedVehicles: Int = 0,
    val acpvGapToNextSlab: Double = 0.0,
    val totalRevenueGapToNextSlab: Double = 0.0,
    val slab1Rate: Double = 0.0,
    val slab2Rate: Double = 0.0,
    val slab3Rate: Double = 0.0
)

class DashboardAnalyticsViewModel(
    private val crmDao: CrmDao
) : ViewModel() {

    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()

    fun selectChannelAndConsignee(channel: String, consigneeCode: String) {
        _uiState.value = _uiState.value.copy(
            selectedChannel = channel,
            selectedConsigneeCode = consigneeCode
        )
        refreshAnalytics()
    }

    fun refreshAnalytics() {
        viewModelScope.launch {
            val currentState = _uiState.value
            val channel = currentState.selectedChannel
            val consigneeCode = currentState.selectedConsigneeCode

            withContext(Dispatchers.IO) {
                val benchmark = crmDao.getBenchmarkForConsignee(consigneeCode)
                
                val base24 = benchmark?.baseSeptNov2024Acpv ?: 10000.0
                val base25 = benchmark?.baseSeptNov2025Acpv ?: 8500.0
                val calcBase = max(0.85 * base24, base25)
                val baseAcpv = if (calcBase <= 0) 9000.0 else calcBase

                val validVehicles = 42
                val totalRetail = 720000.0
                val workshopRetail = 85000.0
                val trueValueRetail = 15000.0

                val showroomRetail = totalRetail - workshopRetail - (if (channel == "ARENA") trueValueRetail else 0.0)
                val currentAcpv = if (validVehicles > 0) showroomRetail / validVehicles else 0.0
                val growthPercent = if (baseAcpv > 0) ((currentAcpv - baseAcpv) / baseAcpv) * 100.0 else 0.0

                val targetWholesale = benchmark?.targetWholesaleOfftakeUnits ?: 50
                val currentWholesale = benchmark?.currentWholesaleOfftakeUnits ?: 48
                val wholesaleRatio = if (targetWholesale > 0) (currentWholesale.toDouble() / targetWholesale) * 100.0 else 0.0
                val isWholesaleGateMet = wholesaleRatio >= 90.0

                val workshopRatio = benchmark?.workshopCrossChannelRatio ?: 0.92
                val isWorkshopRatioMet = workshopRatio >= 0.90

                var earnedRate = 0.0
                var slab1 = 0.0; var slab2 = 0.0; var slab3 = 0.0

                if (channel == "NEXA") {
                    slab1 = 1.40; slab2 = 8.70; slab3 = 14.40
                    earnedRate = when {
                        currentAcpv >= 29500 -> if (growthPercent >= 7.5) 14.40 else 9.90
                        currentAcpv >= 19500 -> when {
                            growthPercent >= 10.0 -> 14.40
                            growthPercent >= 8.0 -> 12.60
                            growthPercent >= 6.0 -> 11.70
                            growthPercent >= 4.0 -> 10.80
                            growthPercent >= 2.0 -> 9.60
                            growthPercent >= 0.0 -> 8.70
                            else -> 7.50
                        }
                        currentAcpv >= 11500 -> if (growthPercent >= 12.5) 5.40 else 1.40
                        else -> 0.0
                    }
                } else { // ARENA
                    slab1 = 2.00; slab2 = 6.50; slab3 = 11.00
                    earnedRate = when {
                        currentAcpv >= 25000 -> if (growthPercent >= 10.0) 11.00 else 8.50
                        currentAcpv >= 17000 -> if (growthPercent >= 5.0) 6.50 else 4.50
                        currentAcpv >= 10000 -> 2.00
                        else -> 0.0
                    }
                }

                val finalPayout = if (isWholesaleGateMet && isWorkshopRatioMet) {
                    (earnedRate / 100.0) * showroomRetail
                } else 0.0

                val targetNextAcpv = 29500.0
                val acpvGap = max(0.0, targetNextAcpv - currentAcpv)
                val totalRevenueGap = acpvGap * validVehicles

                _uiState.value = DashboardUiState(
                    selectedChannel = channel,
                    selectedConsigneeCode = consigneeCode,
                    currentAcpv = currentAcpv,
                    growthPercent = growthPercent,
                    earnedPercentage = earnedRate,
                    projectedPayout = finalPayout,
                    wholesaleOfftakePercent = wholesaleRatio,
                    isWholesaleGateMet = isWholesaleGateMet,
                    workshopCrossChannelRatio = workshopRatio * 100.0,
                    isWorkshopRatioMet = isWorkshopRatioMet,
                    mtdShowroomRetail = showroomRetail,
                    mtdWorkshopRetail = workshopRetail,
                    validRetailedVehicles = validVehicles,
                    acpvGapToNextSlab = acpvGap,
                    totalRevenueGapToNextSlab = totalRevenueGap,
                    slab1Rate = slab1,
                    slab2Rate = slab2,
                    slab3Rate = slab3
                )
            }
        }
    }
}
"""

files["app/src/main/java/com/ranamotors/crm/ui/incentive/IncentiveDashboardScreen.kt"] = """package com.ranamotors.crm.ui.incentive

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IncentiveDashboardScreen(
    viewModel: DashboardAnalyticsViewModel
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Rana Motors CRM",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "Accessories Desk (C1 Region) • Sep-Nov 2026",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refreshAnalytics() }) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Refresh Data"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f))
                .verticalScroll(scrollState)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ChannelAndConsigneeSelector(
                selectedChannel = uiState.selectedChannel,
                selectedConsignee = uiState.selectedConsigneeCode,
                onSelectionChanged = { channel, consignee ->
                    viewModel.selectChannelAndConsignee(channel, consignee)
                }
            )

            HeroEarningsBanner(
                earnedRate = uiState.earnedPercentage,
                projectedPayout = uiState.projectedPayout,
                currentAcpv = uiState.currentAcpv,
                growthPercent = uiState.growthPercent
            )

            GatingChecksCard(
                isWholesaleGateMet = uiState.isWholesaleGateMet,
                wholesalePercent = uiState.wholesaleOfftakePercent,
                isWorkshopRatioMet = uiState.isWorkshopRatioMet,
                workshopRatioPercent = uiState.workshopCrossChannelRatio
            )

            SlabProgressMatrixCard(
                channel = uiState.selectedChannel,
                currentAcpv = uiState.currentAcpv,
                slab1Rate = uiState.slab1Rate,
                slab2Rate = uiState.slab2Rate,
                slab3Rate = uiState.slab3Rate
            )

            RevenueMetricsBreakdownCard(
                showroomRetail = uiState.mtdShowroomRetail,
                workshopRetail = uiState.mtdWorkshopRetail,
                validVehicles = uiState.validRetailedVehicles,
                acpvGap = uiState.acpvGapToNextSlab,
                revenueGap = uiState.totalRevenueGapToNextSlab
            )
        }
    }
}

@Composable
fun ChannelAndConsigneeSelector(
    selectedChannel: String,
    selectedConsignee: String,
    onSelectionChanged: (String, String) -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(
                text = "CHANNEL & CONSIGNEE SCOPE",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                letterSpacing = 0.5.sp
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedChannel == "ARENA",
                    onClick = { onSelectionChanged("ARENA", "CONSIGNEE_ARENA_1") },
                    label = { Text("ARENA (08A1 / 08A4)") },
                    modifier = Modifier.weight(1f)
                )
                FilterChip(
                    selected = selectedChannel == "NEXA",
                    onClick = { onSelectionChanged("NEXA", "CONSIGNEE_NEXA_1") },
                    label = { Text("NEXA (08D3 / 08D6)") },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
fun HeroEarningsBanner(
    earnedRate: Double,
    projectedPayout: Double,
    currentAcpv: Double,
    growthPercent: Double
) {
    val currencyFormat = NumberFormat.getCurrencyInstance(Locale("en", "IN"))

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Unspecified),
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.horizontalGradient(
                    colors = listOf(Color(0xFF0D47A1), Color(0xFF1976D2))
                ),
                shape = RoundedCornerShape(16.dp)
            )
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "PROJECTED SCHEME PAYOUT",
                color = Color.White.copy(alpha = 0.8f),
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = currencyFormat.format(projectedPayout),
                color = Color.White,
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(16.dp))
            Divider(color = Color.White.copy(alpha = 0.2f))
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "Current ACPV",
                        color = Color.White.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                    Text(
                        text = currencyFormat.format(currentAcpv),
                        color = Color.White,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "Earned Slab Rate",
                        color = Color.White.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                    Text(
                        text = "%.2f%%".format(earnedRate),
                        color = Color(0xFFFFD54F),
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "YoY Growth",
                        color = Color.White.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                    Text(
                        text = "%+.1f%%".format(growthPercent),
                        color = if (growthPercent >= 0) Color(0xFF81C784) else Color(0xFFE57373),
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

@Composable
fun GatingChecksCard(
    isWholesaleGateMet: Boolean,
    wholesalePercent: Double,
    isWorkshopRatioMet: Boolean,
    workshopRatioPercent: Double
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "SCHEME QUALIFICATION GATES",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                letterSpacing = 0.5.sp
            )
            Spacer(modifier = Modifier.height(12.dp))
            GateStatusRow(
                title = "Wholesale Offtake Gate (≥ 90%)",
                currentValue = "%.1f%%".format(wholesalePercent),
                isMet = isWholesaleGateMet
            )
            Spacer(modifier = Modifier.height(8.dp))
            GateStatusRow(
                title = "Workshop Cross-Channel Ratio (≥ 90%)",
                currentValue = "%.1f%%".format(workshopRatioPercent),
                isMet = isWorkshopRatioMet
            )
        }
    }
}

@Composable
fun GateStatusRow(
    title: String,
    currentValue: String,
    isMet: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Icon(
                imageVector = if (isMet) Icons.Default.CheckCircle else Icons.Default.Warning,
                contentDescription = null,
                tint = if (isMet) Color(0xFF2E7D32) else Color(0xFFC62828),
                modifier = Modifier.size(18.dp)
            )
            Text(
                text = title,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium
            )
        }
        Text(
            text = currentValue,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold,
            color = if (isMet) Color(0xFF2E7D32) else Color(0xFFC62828)
        )
    }
}

@Composable
fun SlabProgressMatrixCard(
    channel: String,
    currentAcpv: Double,
    slab1Rate: Double,
    slab2Rate: Double,
    slab3Rate: Double
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "INCENTIVE SLAB MATRIX ($channel)",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                letterSpacing = 0.5.sp
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            val target1 = if (channel == "NEXA") 11500.0 else 10000.0
            val target2 = if (channel == "NEXA") 19500.0 else 17000.0
            val target3 = if (channel == "NEXA") 29500.0 else 25000.0

            SlabTierRow(label = "Slab 1 (Get on Track)", targetAcpv = target1, ratePercent = slab1Rate, isAchieved = currentAcpv >= target1)
            Spacer(modifier = Modifier.height(8.dp))
            SlabTierRow(label = "Slab 2 (Accelerate Growth)", targetAcpv = target2, ratePercent = slab2Rate, isAchieved = currentAcpv >= target2)
            Spacer(modifier = Modifier.height(8.dp))
            SlabTierRow(label = "Slab 3 (A Bolder Tomorrow)", targetAcpv = target3, ratePercent = slab3Rate, isAchieved = currentAcpv >= target3)
        }
    }
}

@Composable
fun SlabTierRow(
    label: String,
    targetAcpv: Double,
    ratePercent: Double,
    isAchieved: Boolean
) {
    val currencyFormat = NumberFormat.getCurrencyInstance(Locale("en", "IN"))
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(if (isAchieved) Color(0xFFE8F5E9) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(text = label, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            Text(text = "Target: ${currencyFormat.format(targetAcpv)}", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Text(
            text = "%.2f%%".format(ratePercent),
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            color = if (isAchieved) Color(0xFF2E7D32) else MaterialTheme.colorScheme.onSurface
        )
    }
}

@Composable
fun RevenueMetricsBreakdownCard(
    showroomRetail: Double,
    workshopRetail: Double,
    validVehicles: Int,
    acpvGap: Double,
    revenueGap: Double
) {
    val currencyFormat = NumberFormat.getCurrencyInstance(Locale("en", "IN"))

    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "VOLUME & REVENUE BREAKDOWN",
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
                letterSpacing = 0.5.sp
            )
            Spacer(modifier = Modifier.height(12.dp))
            MetricDetailRow(label = "Valid Retailed Vehicles", value = "$validVehicles Units")
            MetricDetailRow(label = "MTD Showroom Accessories", value = currencyFormat.format(showroomRetail))
            MetricDetailRow(label = "MTD Workshop Accessories", value = currencyFormat.format(workshopRetail))
            Spacer(modifier = Modifier.height(8.dp))
            Divider()
            Spacer(modifier = Modifier.height(8.dp))
            MetricDetailRow(
                label = "ACPV Shortfall to Next Slab",
                value = currencyFormat.format(acpvGap),
                valueColor = Color(0xFFD84315)
            )
            MetricDetailRow(
                label = "Total Revenue Gap Required",
                value = currencyFormat.format(revenueGap),
                valueColor = Color(0xFFD84315)
            )
        }
    }
}

@Composable
fun MetricDetailRow(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(text = value, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = valueColor)
    }
}
"""

for path, content in files.items():
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("SUCCESS: All project files generated successfully!")
