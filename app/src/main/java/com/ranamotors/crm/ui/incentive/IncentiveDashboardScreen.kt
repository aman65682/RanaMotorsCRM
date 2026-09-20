package com.ranamotors.crm.ui.incentive

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
