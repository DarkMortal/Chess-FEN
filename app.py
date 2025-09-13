import os
import traceback
from PIL import Image
from typing import List
import streamlit as st
from main import generate_board_matrix, matrix_to_fen

from edge_detection import _edge_density, _cv2_has_chessboard
IMAGE_SIZE = (1024, 1024) 

def visualizeBoard(board: List[List[str]]):
    for row in board:
        for cell in row:
            if cell is None:
                print(0, end = " ")
            else:
                print(cell, end = " ")
        print()

# Example boards directory
EXAMPLES_DIR = "tests"

st.set_page_config(page_title="Chess FEN Scanner", layout="centered")

st.title("♟️ Chess FEN Scanner")
st.write("Upload a chessboard image to generate its FEN notation.")

# File uploader
uploaded_file = st.file_uploader("Upload a chessboard image", type=["png", "jpg", "jpeg"])

# Example section
st.subheader("📌 Example Boards")
example_files = []
if os.path.exists(EXAMPLES_DIR):
    example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

example_choice = None
if example_files:
    example_choice = st.selectbox("Choose an example board", ["Select an example"] + example_files)

if uploaded_file:
    image_source = uploaded_file
elif example_choice and example_choice != "Select an example":
    image_source = os.path.join(EXAMPLES_DIR, example_choice)
else:
    image_source = None

if image_source:
    try:
        img = Image.open(image_source).convert("RGB").resize(IMAGE_SIZE)
        
        # if not _cv2_has_chessboard(img):
        #   raise Exception("Not a valid image")

        # TODO: fallback to heuristic
        # _edge_density(img)
        
        st.image(img, caption="Selected Chessboard",  width = 'stretch')
        board_matrix = generate_board_matrix(img)

        # Base FEN
        placement = matrix_to_fen(board_matrix)

        if placement is None:
            st.error("Please upload a different image and try again")
        else:
            # Metadata options
            st.subheader("Metadata Options")
            side_to_move = st.radio("Side to move", ["w", "b"])
            castling = ""
            if st.checkbox("White King-side (K)"): castling += "K"
            if st.checkbox("White Queen-side (Q)"): castling += "Q"
            if st.checkbox("Black King-side (k)"): castling += "k"
            if st.checkbox("Black Queen-side (q)"): castling += "q"
            if castling == "": castling = "-"
            en_passant = st.text_input("En passant target square", "-")
            halfmove = st.number_input("Halfmove clock", min_value=0, value=0)
            fullmove = st.number_input("Fullmove number", min_value=1, value=1)

            final_fen = f"{placement} {side_to_move} {castling} {en_passant} {halfmove} {fullmove}"
            st.subheader("Generated FEN")
            st.code(final_fen, language="text")

    except Exception as exc:
        traceback.print_exc()
        st.error(f"{exc}\n Please upload a different image and try again")