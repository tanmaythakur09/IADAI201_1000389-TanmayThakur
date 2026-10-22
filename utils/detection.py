"""
Slot-level detection logic for ParkVision AI — deliberately kept free of
any Streamlit import so it can be unit-tested and reused from the
training notebook or a CLI script, not just the dashboard.
"""

from pathlib import Path

import cv2
import numpy as np

from utils.insights import SlotResult

IMG_SIZE = (224, 224)


def classify_with_model(model, crop_bgr: np.ndarray, conf_threshold: float = 0.5) -> tuple[bool, float]:
    """Occupied/empty classification using the trained MobileNetV2 model.

    The saved model already contains MobileNetV2's preprocessing as its
    first layer, so it is fed raw 0-255 RGB pixels here.
    Class order: label 0 = empty, label 1 = occupied (sigmoid output).
    """
    resized = cv2.resize(crop_bgr, IMG_SIZE)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype("float32")
    batch = rgb[None, ...]
    pred = model.predict(batch, verbose=0)[0]

    if pred.shape[-1] == 1:
        prob_occupied = float(pred[0])
    else:
        prob_occupied = float(pred[1])  # softmax [empty, occupied]

    occupied = prob_occupied >= conf_threshold
    confidence = prob_occupied if occupied else 1 - prob_occupied
    return occupied, confidence


def classify_with_heuristic(crop_bgr: np.ndarray, conf_threshold: float = 0.5) -> tuple[bool, float]:
    """Fallback used only when no trained model is present yet (demo mode).

    Not a real detector — just a texture/edge-density proxy so the UI has
    something plausible to show before training finishes. Empty asphalt is
    comparatively flat; a parked car adds edges and local contrast. Trims a
    margin off each crop first so painted slot-boundary lines (present in
    both the synthetic demo image and real photos) don't get mistaken for
    "occupied" texture.
    """
    h, w = crop_bgr.shape[:2]
    mx, my = int(w * 0.15), int(h * 0.1)
    interior = crop_bgr[my : h - my, mx : w - mx]
    if interior.size == 0:
        interior = crop_bgr

    gray = cv2.cvtColor(interior, cv2.COLOR_BGR2GRAY)
    edge_density = cv2.Laplacian(gray, cv2.CV_64F).var()
    threshold = 100.0 * (conf_threshold / 0.5)
    occupied = edge_density > threshold
    confidence = min(0.5 + abs(edge_density - threshold) / 1500, 0.95)
    return occupied, confidence


def run_inference(image_bgr: np.ndarray, positions: list, model=None, conf_threshold: float = 0.5) -> list[SlotResult]:
    results = []
    for slot in positions:
        x, y, w, h = slot["x"], slot["y"], slot["w"], slot["h"]
        crop = image_bgr[y : y + h, x : x + w]
        if crop.size == 0:
            continue
        if model is not None:
            occupied, confidence = classify_with_model(model, crop, conf_threshold=conf_threshold)
        else:
            occupied, confidence = classify_with_heuristic(crop, conf_threshold=conf_threshold)
        results.append(SlotResult(slot_id=slot["id"], occupied=occupied, confidence=confidence))
    return results


def draw_overlay(
    image_bgr: np.ndarray,
    positions: list,
    results: list[SlotResult],
    show_ids: bool = True,
    show_conf: bool = True,
) -> np.ndarray:
    annotated = image_bgr.copy()
    by_id = {r.slot_id: r for r in results}
    for slot in positions:
        r = by_id.get(slot["id"])
        if r is None:
            continue
        x, y, w, h = slot["x"], slot["y"], slot["w"], slot["h"]
        color = (0, 0, 255) if r.occupied else (0, 200, 0)  # BGR: red / green
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 3)

        label_parts = []
        if show_ids:
            label_parts.append(f"#{r.slot_id}")
        label_parts.append("OCC" if r.occupied else "FREE")
        if show_conf:
            label_parts.append(f"{int(r.confidence * 100)}%")

        label = " ".join(label_parts)
        cv2.putText(annotated, label, (x + 4, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
    return annotated

