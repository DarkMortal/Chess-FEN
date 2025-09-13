import numpy as np
from PIL import Image
import tensorflow.python.keras as tf_keras
from tensorflow.python.keras.models import load_model

from tensorflow.python.keras.engine import data_adapter

from keras import __version__
tf_keras.__version__ = __version__

def _is_distributed_dataset(ds):
    return isinstance(ds, data_adapter.input_lib.DistributedDatasetSpec)

data_adapter._is_distributed_dataset = _is_distributed_dataset

MODEL_PATH = "trained_models/chess_piece_color_model.h5"
predictionModel = load_model(MODEL_PATH)
print("✅ Model loaded successfully!")

IMAGE_SIZE = (128, 128)   # must match training
THRESHOLD = 0.7           # min confidence to consider non-empty
pieces = ["pawn", "rook", "knight", "bishop", "queen", "king"]
colors = ["black", "white"]

# FEN mapping
fen_map = {
    ("pawn", "white"): "P",
    ("rook", "white"): "R",
    ("knight", "white"): "N",
    ("bishop", "white"): "B",
    ("queen", "white"): "Q",
    ("king", "white"): "K",
    ("pawn", "black"): "p",
    ("rook", "black"): "r",
    ("knight", "black"): "n",
    ("bishop", "black"): "b",
    ("queen", "black"): "q",
    ("king", "black"): "k",
}

def load_image(path):
    img = Image.open(path).convert("RGB").resize(IMAGE_SIZE)
    return np.array(img, dtype=np.float32) / 255.0

def predict_image(img_path, model):
    img = load_image(img_path)
    arr = np.expand_dims(img, axis=0)
    piece_pred, color_pred = model.predict(arr)
    piece = pieces[np.argmax(piece_pred[0])]
    color = colors[np.argmax(color_pred[0])]
    return piece, color

def preprocess(img, size = IMAGE_SIZE):
    img = img.resize(size).convert("RGB")
    arr = np.array(img, dtype = np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def predict_square(img):
    arr = preprocess(img)
    piece_pred, color_pred = predictionModel.predict(arr, verbose = 0)

    piece_idx = np.argmax(piece_pred[0])
    color_idx = np.argmax(color_pred[0])
    piece_conf = piece_pred[0][piece_idx]
    color_conf = color_pred[0][color_idx]

    # If low confidence -> empty square
    if piece_conf < THRESHOLD or color_conf < THRESHOLD:
        return "."

    piece = pieces[piece_idx]
    color = colors[color_idx]
    return fen_map[(piece, color)]

def generate_board_matrix(board_img):
    w, h = board_img.size
    if w != h:
        return None
    sq_w, sq_h = w // 8, h // 8

    board_matrix = []
    for row in range(8):
        row_pieces = []
        for col in range(8):
            square = board_img.crop((col * sq_w, row * sq_h, (col + 1) * sq_w, (row + 1) * sq_h))
            prediction = predict_square(square)
            print(prediction)
            row_pieces.append(prediction)
        board_matrix.append(row_pieces)
    
    return board_matrix

def matrix_to_fen(board_matrix):
    print(board_matrix)
    fen_rows = []
    for row in board_matrix:
        fen_row = ""
        empty_count = 0
        for cell in row:
            if cell == ".":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    return "/".join(fen_rows)

# Example
# print(predict_image("tests/Example 1.png", predictionModel))