package com.ranamotors.crm.data.local.dao

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
