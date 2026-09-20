package com.ranamotors.crm.data.local.entity

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
