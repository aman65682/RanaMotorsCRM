package com.ranamotors.crm.data.local

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
