package com.ranamotors.crm

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
