#!/usr/bin/env python3
"""
flatten_and_copy.py

Copy (not move) images from:
  dataset/{style}/{theme}/{piece}/{color}/Piece_x.png
into:
  flattened_dataset/{piece}/{color}/Piece_n.png

Usage:
  python3 "Flat Folder.py"
"""

from pathlib import Path
import shutil, re, sys

# ----------- CONFIG -------------
SRC_DIR = Path("")                      # <-- original nested dataset root
DST_DIR = Path("flattened_dataset")     # <-- flattened copy destination
DRY_RUN = False                         # True = don't actually copy, just print actions
# Allowed image extensions (lowercase)
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff"}
# Expected piece/color names (lowercase)
PIECES = {"pawn", "rook", "knight", "bishop", "queen", "king"}
COLORS = {"black", "white"}
# ---------------------------------

SRC_DIR = SRC_DIR.expanduser().resolve()
DST_DIR = DST_DIR.expanduser().resolve()

if not SRC_DIR.exists():
    print(f"ERROR: source directory does not exist: {SRC_DIR}")
    sys.exit(1)

DST_DIR.mkdir(parents=True, exist_ok=True)

# Initialize counters from existing files in DST_DIR (so repeated runs don't overwrite)
counter = {}
for piece in PIECES:
    for color in COLORS:
        d = DST_DIR / piece / color
        if d.exists():
            nums = []
            for f in d.iterdir():
                if not f.is_file(): 
                    continue
                m = re.search(r'Piece_(\d+)', f.name)
                if m:
                    nums.append(int(m.group(1)))
            counter[(piece, color)] = max(nums) if nums else 0
        else:
            counter[(piece, color)] = 0

files_found = 0
files_copied = 0
files_skipped = 0
copied_examples = []
skipped_examples = []

# Walk recursively and find files whose path contains "<piece>/<color>/..."
for file in SRC_DIR.rglob("*"):
    if not file.is_file():
        continue
    if file.suffix.lower() not in ALLOWED_EXT:
        continue

    parts = [p.strip().lower() for p in file.parts]  # normalize
    # look for a segment that is a piece and the next segment a color
    matched = False
    for i in range(len(parts) - 1):
        if parts[i] in PIECES and parts[i + 1] in COLORS:
            piece = parts[i]
            color = parts[i + 1]
            matched = True
            break

    if not matched:
        files_skipped += 1
        if len(skipped_examples) < 5:
            skipped_examples.append(str(file))
        continue

    files_found += 1

    dst_dir = DST_DIR / piece / color
    dst_dir.mkdir(parents=True, exist_ok=True)

    counter[(piece, color)] += 1
    dst_name = f"Piece_{counter[(piece, color)]}{file.suffix.lower()}"
    dst_path = dst_dir / dst_name

    if DRY_RUN:
        print(f"[DRY] {file} -> {dst_path}")
        files_copied += 1
        if len(copied_examples) < 5:
            copied_examples.append(str(dst_path))
        continue

    try:
        shutil.copy2(file, dst_path)
        files_copied += 1
        if len(copied_examples) < 5:
            copied_examples.append(str(dst_path))
    except Exception as e:
        print(f"Failed to copy {file} -> {dst_path}: {e}")

# Summary
print("---- SUMMARY ----")
print(f"Source root : {SRC_DIR}")
print(f"Destination : {DST_DIR}")
print(f"Files matching piece/color pattern : {files_found}")
print(f"Files copied : {files_copied}")
print(f"Files skipped (didn't match expected folders) : {files_skipped}")
if copied_examples:
    print("Examples copied:")
    for p in copied_examples:
        print("  ", p)
if skipped_examples:
    print("Examples skipped (no piece/color pair found in path):")
    for p in skipped_examples:
        print("  ", p)

if files_found == 0:
    print("\nNo matching files were found. Things to check:")
    print("- Are your images actually under paths like: style/theme/<piece>/<color>/file.png ?")
    print("- Are piece folders named exactly (pawn, rook, knight, bishop, queen, king)?")
    print("- Are color folders named exactly 'black' or 'white' (case/space tolerant)?")
    print("- Do your images use extensions other than the allowed ones? Update ALLOWED_EXT if needed.")
    print("- If you prefer a dry-run first, set DRY_RUN = True at the top and re-run.")