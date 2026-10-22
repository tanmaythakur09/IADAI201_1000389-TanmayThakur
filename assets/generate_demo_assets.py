"""
One-off helper that generates a synthetic parking-lot image + matching
slot_positions JSON, purely so app.py has something to run against
before you've trained a real model or sourced a real PKLot photo.

Not part of the assignment pipeline — just a placeholder/demo asset
generator. Replace assets/demo_parking_lot.jpg and
assets/slot_positions_demo.json with a real PKLot image + coordinates
(see slot_position_picker.py) once you have a trained model.

Run:  python assets/generate_demo_assets.py
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).parent
IMG_PATH = OUT_DIR / "demo_parking_lot.jpg"
POS_PATH = OUT_DIR / "slot_positions_demo.json"

random.seed(7)

W, H = 900, 560
img = Image.new("RGB", (W, H), (84, 110, 92))  # asphalt-ish green-grey
draw = ImageDraw.Draw(img)

# lane marking down the middle
draw.rectangle([0, H // 2 - 4, W, H // 2 + 4], fill=(230, 230, 210))

slot_w, slot_h = 110, 170
margin_x, gap_x = 40, 20
rows_y = [40, H - 40 - slot_h]

positions = []
slot_id = 0
for row_y in rows_y:
    x = margin_x
    while x + slot_w <= W - margin_x:
        positions.append({"id": slot_id, "x": x, "y": row_y, "w": slot_w, "h": slot_h})
        # slot line markings
        draw.rectangle([x, row_y, x + slot_w, row_y + slot_h], outline=(230, 230, 210), width=3)
        slot_id += 1
        x += slot_w + gap_x

# randomly "park" cars in about 60% of slots
car_colors = [(178, 34, 34), (25, 25, 112), (47, 79, 79), (160, 160, 160), (90, 60, 20)]
occupied_ids = set(random.sample(range(len(positions)), k=int(len(positions) * 0.6)))

for p in positions:
    if p["id"] in occupied_ids:
        pad = 12
        cx0, cy0 = p["x"] + pad, p["y"] + pad
        cx1, cy1 = p["x"] + p["w"] - pad, p["y"] + p["h"] - pad
        color = random.choice(car_colors)
        draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14, fill=color)
        # windshield
        draw.rectangle([cx0 + 10, cy0 + 15, cx1 - 10, cy0 + 45], fill=(200, 220, 230))

img.save(IMG_PATH, quality=90)

with open(POS_PATH, "w") as f:
    json.dump(positions, f, indent=2)

print(f"Wrote {IMG_PATH} and {POS_PATH} ({len(positions)} slots, {len(occupied_ids)} occupied)")
