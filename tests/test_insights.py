"""
Unit tests for parking lot insight thresholds and summaries.
Validates the hard constraint: Low < 40%, Moderate 40-75%, High > 75%.
"""

import pytest
from utils.insights import classify_congestion, summarize_lot, SlotResult


class TestInsightsThresholds:
    def test_threshold_boundaries(self):
        # 39.9 -> Low (<40%)
        assert classify_congestion(39.9) == "Low"

        # 40.0 -> Moderate (40-75%)
        assert classify_congestion(40.0) == "Moderate"

        # 75.0 -> Moderate (40-75%)
        assert classify_congestion(75.0) == "Moderate"

        # 75.1 -> High (>75%)
        assert classify_congestion(75.1) == "High"

    def test_extreme_boundaries(self):
        assert classify_congestion(0.0) == "Low"
        assert classify_congestion(100.0) == "High"

    def test_summarize_lot(self):
        # 10 slots: 4 occupied = 40% -> Moderate
        results = [
            SlotResult(slot_id=i, occupied=(i < 4), confidence=0.95)
            for i in range(10)
        ]
        summary = summarize_lot(results)
        assert summary.total_slots == 10
        assert summary.occupied_slots == 4
        assert summary.available_slots == 6
        assert summary.occupancy_pct == 40.0
        assert summary.congestion == "Moderate"
        assert "6 slots left" in summary.recommendation

        # 10 slots: 8 occupied = 80% -> High
        results_high = [
            SlotResult(slot_id=i, occupied=(i < 8), confidence=0.95)
            for i in range(10)
        ]
        summary_high = summarize_lot(results_high)
        assert summary_high.occupancy_pct == 80.0
        assert summary_high.congestion == "High"
        assert "2 slot(s) left" in summary_high.recommendation

        # 10 slots: 10 occupied = 100% -> High (Parking full)
        results_full = [
            SlotResult(slot_id=i, occupied=True, confidence=0.99)
            for i in range(10)
        ]
        summary_full = summarize_lot(results_full)
        assert summary_full.available_slots == 0
        assert summary_full.congestion == "High"
        assert "Parking full" in summary_full.recommendation


class TestPdfExportSanitization:
    def test_sanitize_unicode_characters(self):
        from utils.export import sanitize_for_pdf
        sample = "Plenty of space — 12 slots open. “Quote” & en–dash • bullet → arrow"
        sanitized = sanitize_for_pdf(sample)
        assert "—" not in sanitized
        assert "–" not in sanitized
        assert "“" not in sanitized
        assert "”" not in sanitized
        # Verify it encodes to pure ASCII / Latin-1 without error
        sanitized.encode("latin-1")

    def test_generate_pdf_report_success(self):
        from PIL import Image
        from utils.export import generate_pdf_report
        # Create dummy summary with em-dash recommendation
        results = [
            SlotResult(slot_id=1, occupied=False, confidence=0.95),
            SlotResult(slot_id=2, occupied=True, confidence=0.92),
        ]
        summary = summarize_lot(results)
        img = Image.new("RGB", (200, 200), color=(50, 100, 150))
        pdf_bytes = generate_pdf_report(summary, img, image_name="test_lot.jpg")
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")


class TestRealLotAnalysis:
    def test_real_lot_analysis_exact_counts(self):
        import cv2
        import json
        import tensorflow as tf
        from utils.detection import run_inference
        from utils.insights import summarize_lot

        with open("assets/real_slot_positions.json", "r", encoding="utf-8") as f:
            positions = json.load(f)
        img = cv2.imread("assets/real_lot.jpg")
        model = tf.keras.models.load_model("model/parking_classifier.keras")
        results = run_inference(img, positions, model=model, conf_threshold=0.5)
        summary = summarize_lot(results)
        assert summary.total_slots == 40
        assert summary.occupied_slots == 28
        assert summary.available_slots == 12
        assert summary.occupancy_pct == 70.0


