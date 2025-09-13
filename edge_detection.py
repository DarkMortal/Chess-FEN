import cv2
from PIL import Image, ImageFilter
import numpy as np

# TODO: detect if it is actually a chess board and not some cat dog or human
def _cv2_has_chessboard(pil_img):
    try:
        arr = np.asarray(pil_img.convert("L"))
        # OpenCV expects size (columns, rows) of inner corners: 7x7 for an 8x8 squares board
        pattern_size = (7, 7)
        found, corners = cv2.findChessboardCorners(arr, pattern_size, flags = cv2.CALIB_CB_NORMALIZE_IMAGE)
        print("Image corner data:"); print(corners)
        return bool(found)
    except Exception as exc:
        print(exc)
        return False
    
# Edge/heuristic thresholds (tweakable)
EDGE_MAG_THRESHOLD = 30            # per-pixel magnitude to count as an "edge"
MIN_EDGE_DENSITY = 0.01           # too few edges -> probably not a board
MAX_EDGE_DENSITY = 0.60           # too many edges -> textured image (cat), reject
MIN_NONEMPTY_PIECES = 2
MAX_NONEMPTY_PIECES = 32
MIN_BOARD_PIXEL_SIZE = 160         # if board image is too small, reject

def _edge_magnitude_map(pil_gray):
    """Compute a simple Sobel-like magnitude using PIL kernels (returns numpy float array)."""
    # Sobel kernels
    kx = ImageFilter.Kernel((3,3), [-1,0,1,-2,0,2,-1,0,1], scale=1)
    ky = ImageFilter.Kernel((3,3), [-1,-2,-1,0,0,0,1,2,1], scale=1)
    gx_img = pil_gray.filter(kx)
    gy_img = pil_gray.filter(ky)
    gx = np.asarray(gx_img, dtype=np.float32)
    gy = np.asarray(gy_img, dtype=np.float32)
    mag = np.sqrt(gx*gx + gy*gy)
    return mag

def _edge_density(pil_img):
    """Return fraction of pixels with magnitude > EDGE_MAG_THRESHOLD (0..1)."""
    gray = pil_img.convert("L")
    mag = _edge_magnitude_map(gray)
    edge_density = float(np.mean(mag > EDGE_MAG_THRESHOLD))
    if edge_density < MIN_EDGE_DENSITY:
        raise Exception(f"Too few edges ({edge_density:.3f}) — not a chessboard.")
    if edge_density > MAX_EDGE_DENSITY:
        raise Exception(f"Image too textured ({edge_density:.3f}) — not a chessboard.")