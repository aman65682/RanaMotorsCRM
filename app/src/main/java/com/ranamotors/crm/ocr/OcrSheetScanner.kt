package com.ranamotors.crm.ocr

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
        val lines = text.split("
")
        var phone = ""
        var customerName = ""
        var accessoriesAmount = 0.0

        val phoneRegex = Regex("(?:\+91[\s-]*)?[6-9]\d{9}")
        val amountRegex = Regex("(?:Rs\.?|INR|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)")

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
