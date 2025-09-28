import os
from PIL import Image

# Input image path
style_name = "Collins"
theme = "Brown"
current_dir = os.path.dirname(os.path.abspath(__file__))
input_image = os.path.join(current_dir, f"Board/{style_name}/{theme}.png")

# Piece mapping according to standard chess notation
piece_map = {
    "P": "pawn",
    "R": "rook",
    "N": "knight",
    "B": "bishop",
    "Q": "queen",
    "K": "king"
}

# Initial board placement (FEN format equivalent)
initial_board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],  # 8th rank (black back row)
    ["p"] * 3 + ["K", "Q"] + ["p"] * 3,        # 7th rank (black pawns)
    [None] * 8,                                # 6th
    [None] * 8,                                # 5th
    [None] * 8,                                # 4th
    [None] * 8,                                # 3rd
    ["P"] * 3 + ["k", "q"] + ["P"] * 3,        # 2nd rank (white pawns)
    ["R", "N", "B", "Q", "K", "B", "N", "R"],  # 1st rank (white back row)
]

# Function to save extracted piece
def save_piece(img, piece_name, color, count):
    folder_path = f"Pieces/{style_name}/{theme}/{piece_name}/{color}"
    os.makedirs(folder_path, exist_ok=True)
    file_path = f"{folder_path}/Piece_{count}.png"
    img.save(file_path)

# Load image
image = Image.open(input_image)
width, height = image.size

# Each square size
square_w = width // 8
square_h = height // 8

# Counters for each piece
piece_counters = {}
pawn_squares_saved = {
    "black": {"dark": False, "light": False},
    "white": {"dark": False, "light": False}
}

# Function to check square color (dark or light)
square_color = lambda row, col: "dark" if (row + col) % 2 == 1 else "light"

# Loop through the board and extract pieces
for row in range(8):
    for col in range(8):
        piece = initial_board[row][col]
        if piece:
            # Determine color
            color = "black" if piece.islower() else "white"
            piece_name = piece_map[piece.upper()]

            # Special handling for pawns
            if piece_name == "pawn":
                sq_color = square_color(row, col)

                # Skip if we already have one pawn of this color on this type of square
                if pawn_squares_saved[color][sq_color]:
                    continue
                pawn_squares_saved[color][sq_color] = True

            # Crop the square
            left = col * square_w
            upper = row * square_h
            right = left + square_w
            lower = upper + square_h
            cropped = image.crop((left, upper, right, lower))

            # Track number
            piece_counters.setdefault((piece_name, color), 0)
            piece_counters[(piece_name, color)] += 1
            count = piece_counters[(piece_name, color)]

            # Save the piece
            save_piece(cropped, piece_name, color, count)

print("✅ Extraction completed! Only 1 pawn per color saved.")
