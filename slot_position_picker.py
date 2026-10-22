"""
Interactive tool to mark parking-slot rectangles on a reference photo of
YOUR parking lot, and save them to a slot_positions.json that app.py (and
the notebook, if you want to re-crop for more training data) can read.

Slot positions are tied to ONE fixed camera angle — exactly like the real
PKLot cameras (PUC / UFPR04 / UFPR05) each have their own fixed layout.
Re-run this once per camera view.

--------------------------------------------------------------------------
USAGE A — local machine (OpenCV window, click-and-drag):

    python slot_position_picker.py --image path/to/your_lot.jpg \
        --out slot_positions.json

    - Left-click a slot's top-left corner, drag to the bottom-right
      corner, release. A green box is added.
    - Press 'u' to undo the last box.
    - Press 's' to save and quit. Press 'q' to quit without saving.

USAGE B — Google Colab (no GUI window available):
    cv2.imshow doesn't work in Colab. Instead, use the matplotlib-based
    helper `pick_positions_matplotlib()` below in a notebook cell — it
    shows the image with a pixel-coordinate grid so you can read off
    corners by eye and type them in. See the notebook's final cells for
    a worked example.
--------------------------------------------------------------------------
"""

import argparse
import json

import cv2


def pick_positions_cv2(image_path: str, out_path: str) -> None:
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    clone = image.copy()
    positions = []
    drawing = {"start": None}

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing["start"] = (x, y)
        elif event == cv2.EVENT_LBUTTONUP and drawing["start"] is not None:
            x0, y0 = drawing["start"]
            x1, y1 = min(x0, x), min(y0, y)
            w, h = abs(x - x0), abs(y - y0)
            if w > 5 and h > 5:
                positions.append({"id": len(positions), "x": x1, "y": y1, "w": w, "h": h})
            drawing["start"] = None
        redraw()

    def redraw():
        img = clone.copy()
        for p in positions:
            cv2.rectangle(img, (p["x"], p["y"]), (p["x"] + p["w"], p["y"] + p["h"]), (0, 255, 0), 2)
            cv2.putText(img, str(p["id"]), (p["x"] + 4, p["y"] + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("slot picker", img)

    cv2.namedWindow("slot picker")
    cv2.setMouseCallback("slot picker", on_mouse)
    redraw()
    print("Drag a box per slot. 'u' = undo last, 's' = save & quit, 'q' = quit without saving.")

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key == ord("u") and positions:
            positions.pop()
            redraw()
        elif key == ord("s"):
            with open(out_path, "w") as f:
                json.dump(positions, f, indent=2)
            print(f"Saved {len(positions)} slots to {out_path}")
            break
        elif key == ord("q"):
            print("Quit without saving.")
            break

    cv2.destroyAllWindows()


def pick_positions_matplotlib(image_path: str):
    """Colab-friendly alternative: displays the image with a coordinate
    grid overlaid so you can read off (x, y) pixel corners by eye, then
    build the positions list yourself, e.g.:

        positions = [
            {"id": 0, "x": 40, "y": 40, "w": 110, "h": 170},
            {"id": 1, "x": 170, "y": 40, "w": 110, "h": 170},
            ...
        ]
        import json
        json.dump(positions, open("slot_positions.json", "w"), indent=2)

    Call this from a notebook cell: `pick_positions_matplotlib("lot.jpg")`
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(50))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(50))
    ax.grid(color="yellow", linestyle="--", linewidth=0.5)
    plt.title("Read (x, y) pixel coordinates off the grid for each slot corner")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mark parking-slot rectangles on a reference image.")
    parser.add_argument("--image", required=True, help="Path to a reference photo of the parking lot")
    parser.add_argument("--out", default="slot_positions.json", help="Where to save the resulting JSON")
    args = parser.parse_args()
    pick_positions_cv2(args.image, args.out)
