package com.ranamotors.crm.ui.incentive

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
